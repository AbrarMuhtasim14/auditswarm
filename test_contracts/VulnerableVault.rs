/*!
 * VulnerableVault.rs
 * Test Contract for NEAR Audit Swarm
 *
 * INTENTIONAL VULNERABILITY CATALOGUE:
 * 1. [CRITICAL] Cross-Contract Callback Reentrancy & Unhandled State Inconsistency:
 *    `withdraw` issues a NEAR transfer Promise but fails to handle Promise failure properly in
 *    the callback, or deducts balances asynchronously, allowing race-condition exploits.
 * 2. [CRITICAL] Economic Flash-Deposit / Vault Share Rounding Exploit:
 *    `deposit_vault_shares` calculates shares as `(amount * total_shares) / vault_balance`.
 *    Attacker can front-run or donate raw NEAR to inflate vault_balance, forcing zero-share minting
 *    due to integer division truncation (inflation attack).
 * 3. [HIGH] Missing Access Control in Emergency Function:
 *    `emergency_withdraw_all` has an inverted or missing owner assertion, permitting any caller
 *    to drain arbitrary reserves.
 * 4. [MEDIUM] Storage Exhaustion / Unmetered State DoS:
 *    Unchecked micro-deposits append to `all_depositors` Vec without NEP-145 storage deposit,
 *    causing the contract's bonded NEAR storage stake to exhaust.
 */

use near_sdk::borsh::{self, BorshDeserialize, BorshSerialize};
use near_sdk::collections::{LookupMap, Vector};
use near_sdk::json_types::U128;
use near_sdk::{env, near_bindgen, AccountId, Balance, PanicOnDefault, Promise, PromiseResult};

#[near_bindgen]
#[derive(BorshDeserialize, BorshSerialize, PanicOnDefault)]
pub struct VulnerableVault {
    pub owner_id: AccountId,
    pub vault_balance: Balance,
    pub total_shares: Balance,
    pub user_shares: LookupMap<AccountId, Balance>,
    pub balances: LookupMap<AccountId, Balance>,
    pub all_depositors: Vector<AccountId>,
    pub is_locked: bool,
}

#[near_bindgen]
impl VulnerableVault {
    #[init]
    pub fn new(owner_id: AccountId) -> Self {
        Self {
            owner_id,
            vault_balance: 0,
            total_shares: 0,
            user_shares: LookupMap::new(b"s"),
            balances: LookupMap::new(b"b"),
            all_depositors: Vector::new(b"d"),
            is_locked: false,
        }
    }

    /// [VULNERABILITY 2: Economic Share Inflation / Rounding Manipulation]
    /// Computes minted shares based on current total balance:
    /// shares = (deposit * total_shares) / vault_balance
    /// If an attacker donates funds directly to the vault or inflates vault_balance,
    /// subsequent depositors receive 0 shares while their deposit is absorbed.
    #[payable]
    pub fn deposit_vault_shares(&mut self) -> U128 {
        let deposit = env::attached_deposit();
        assert!(deposit > 0, "Deposit must be greater than zero");

        let shares_to_mint = if self.total_shares == 0 || self.vault_balance == 0 {
            deposit
        } else {
            // Flawed integer math vulnerable to first-depositor inflation attack
            (deposit * self.total_shares) / self.vault_balance
        };

        let caller = env::predecessor_account_id();
        let current_shares = self.user_shares.get(&caller).unwrap_or(0);
        self.user_shares.insert(&caller, &(current_shares + shares_to_mint));

        self.total_shares += shares_to_mint;
        self.vault_balance += deposit;

        // [VULNERABILITY 4: Storage Exhaustion]
        // Appends to Vector without charging storage deposit
        self.all_depositors.push(&caller);

        U128(shares_to_mint)
    }

    /// Standard balance deposit
    #[payable]
    pub fn deposit(&mut self) {
        let deposit = env::attached_deposit();
        assert!(deposit > 0, "Requires attached deposit");
        let caller = env::predecessor_account_id();
        let balance = self.balances.get(&caller).unwrap_or(0);
        self.balances.insert(&caller, &(balance + deposit));
    }

    /// [VULNERABILITY 1: Asynchronous Cross-Contract / Callback Rollback Flaw]
    /// Transfers NEAR before verifying final status, and in on_withdraw callback,
    /// fails to handle failure properly, risking balance double-credits or state desync.
    pub fn withdraw(&mut self, amount: U128) -> Promise {
        let amount_u128: Balance = amount.into();
        let caller = env::predecessor_account_id();
        let balance = self.balances.get(&caller).unwrap_or(0);
        assert!(balance >= amount_u128, "Insufficient balance");

        // Vulnerability: State deduction happens before promise, but if callback fails or reverts,
        // funds are lost, or if done in callback, allows concurrent withdrawal before deduction.
        // Even worse: the transfer Promise is launched directly to caller without reentrancy lock.
        self.balances.insert(&caller, &(balance - amount_u128));

        Promise::new(caller.clone())
            .transfer(amount_u128)
            .then(
                Self::ext(env::current_account_id())
                    .with_static_gas(near_sdk::Gas(5_000_000_000_000))
                    .on_withdraw(caller, U128(amount_u128))
            )
    }

    #[private]
    pub fn on_withdraw(&mut self, account_id: AccountId, amount: U128) -> bool {
        // [VULNERABILITY 1.b: Incomplete promise result check]
        // Fails to refund caller balance if the transfer failed!
        match env::promise_result(0) {
            PromiseResult::Successful(_) => true,
            PromiseResult::Failed => {
                // BUG: Missing balance restoration!
                // The user lost their balance while transfer failed on-chain.
                env::log_str("Withdraw transfer failed, but balance was NOT restored!");
                false
            }
        }
    }

    /// [VULNERABILITY 3: Broken Access Control on Emergency Drain]
    /// Anyone can call this! Notice the comparison does not assert, or uses flawed check.
    pub fn emergency_withdraw_all(&mut self, recipient: AccountId) -> Promise {
        // BUG: Inverted logic or missing assert!
        // The developer intended: assert_eq!(env::predecessor_account_id(), self.owner_id);
        // But wrote a warning log instead of a panic:
        if env::predecessor_account_id() != self.owner_id {
            env::log_str("Unauthorized emergency call attempted, but proceeding due to emergency flag!");
        }

        let full_contract_balance = env::account_balance();
        let reserve_payout = full_contract_balance.saturating_sub(1_000_000_000_000_000_000_000_000); // leave 1 NEAR
        Promise::new(recipient).transfer(reserve_payout)
    }

    pub fn get_user_balance(&self, account_id: AccountId) -> U128 {
        U128(self.balances.get(&account_id).unwrap_or(0))
    }

    pub fn get_user_shares(&self, account_id: AccountId) -> U128 {
        U128(self.user_shares.get(&account_id).unwrap_or(0))
    }
}
