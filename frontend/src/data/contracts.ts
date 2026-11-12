export interface ContractSample {
  id: string;
  name: string;
  description: string;
  code: string;
  expected_vulnerabilities: string[];
}

export const VULNERABLE_VAULT_CODE = `/*!
 * VulnerableVault.rs
 * Test Contract for NEAR Audit Swarm
 *
 * INTENTIONAL VULNERABILITY CATALOGUE:
 * 1. [CRITICAL] Cross-Contract Callback Reentrancy & Unhandled State Inconsistency:
 *    withdraw issues a NEAR transfer Promise but fails to handle Promise failure properly in
 *    the callback, or deducts balances asynchronously, allowing race-condition exploits.
 * 2. [CRITICAL] Economic Flash-Deposit / Vault Share Rounding Exploit:
 *    deposit_vault_shares calculates shares as (amount * total_shares) / vault_balance.
 *    Attacker can front-run or donate raw NEAR to inflate vault_balance, forcing zero-share minting
 *    due to integer division truncation (inflation attack).
 * 3. [HIGH] Missing Access Control in Emergency Function:
 *    emergency_withdraw_all has an inverted or missing owner assertion, permitting any caller
 *    to drain arbitrary reserves.
 * 4. [MEDIUM] Storage Exhaustion / Unmetered State DoS:
 *    Unchecked micro-deposits append to all_depositors Vec without NEP-145 storage deposit,
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
}`;

export const SECURE_ESCROW_CODE = `/*!
 * SecureEscrow.rs
 * Test Contract for NEAR Audit Swarm
 *
 * SECURITY DESIGN & BEST PRACTICES:
 * 1. [Checks-Effects-Interactions]: State transitions execute prior to external Promise calls.
 * 2. [Safe Promise Callbacks]: #[private] decorator on callbacks with comprehensive
 *    PromiseResult pattern matching, restoring state safely upon external failure.
 * 3. [Robust Access Control]: Strict assertion of env::predecessor_account_id(), one-yocto
 *    deposit guards (assert_at_least_one_yocto()), and 2-step role management.
 * 4. [NEP-145 Storage Accounting]: Storage bounds verified; users must bond storage before state creation.
 * 5. [Overflow Resistance]: Checked arithmetic with checked_add, checked_sub, and saturating_mul.
 * 6. [NEP-297 Standard Events]: Emits structured JSON logs for indexing and transparency.
 */

use near_sdk::borsh::{self, BorshDeserialize, BorshSerialize};
use near_sdk::collections::{LookupMap, UnorderedMap};
use near_sdk::json_types::U128;
use near_sdk::serde::{Deserialize, Serialize};
use near_sdk::{
    assert_one_yocto, env, near_bindgen, require, AccountId, Balance, Gas, PanicOnDefault,
    Promise, PromiseResult,
};

const GAS_FOR_RESOLVE_PAYOUT: Gas = Gas(10_000_000_000_000); // 10 Tgas
const MIN_STORAGE_BALANCE: Balance = 10_000_000_000_000_000_000_000; // 0.01 NEAR

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, PartialEq, Eq, Debug, Clone)]
#[serde(crate = "near_sdk::serde")]
pub enum EscrowStatus {
    Created,
    Funded,
    WorkSubmitted,
    Completed,
    Refunded,
    Disputed,
}

#[derive(BorshDeserialize, BorshSerialize, Serialize, Deserialize, Clone)]
#[serde(crate = "near_sdk::serde")]
pub struct EscrowAgreement {
    pub agreement_id: u64,
    pub buyer: AccountId,
    pub seller: AccountId,
    pub arbiter: AccountId,
    pub amount: Balance,
    pub status: EscrowStatus,
    pub created_at_block: u64,
    pub completion_evidence_hash: Option<String>,
}

#[near_bindgen]
#[derive(BorshDeserialize, BorshSerialize, PanicOnDefault)]
pub struct SecureEscrow {
    pub admin: AccountId,
    pub next_agreement_id: u64,
    pub agreements: UnorderedMap<u64, EscrowAgreement>,
    pub storage_deposits: LookupMap<AccountId, Balance>,
    pub total_locked_funds: Balance,
}

#[near_bindgen]
impl SecureEscrow {
    #[init]
    pub fn new(admin: AccountId) -> Self {
        require!(!env::state_exists(), "Already initialized");
        Self {
            admin,
            next_agreement_id: 1,
            agreements: UnorderedMap::new(b"a"),
            storage_deposits: LookupMap::new(b"s"),
            total_locked_funds: 0,
        }
    }

    /// Register storage deposit compliant with NEP-145 storage management
    #[payable]
    pub fn storage_deposit(&mut self, account_id: Option<AccountId>) -> U128 {
        let deposit = env::attached_deposit();
        require!(deposit >= MIN_STORAGE_BALANCE, "Deposit below minimum storage requirement");

        let target = account_id.unwrap_or_else(env::predecessor_account_id);
        let current = self.storage_deposits.get(&target).unwrap_or(0);
        let updated = current.checked_add(deposit).expect("Storage deposit overflow");
        self.storage_deposits.insert(&target, &updated);

        U128(updated)
    }

    /// Create and fund a secure escrow agreement atomically
    #[payable]
    pub fn create_agreement(
        &mut self,
        seller: AccountId,
        arbiter: AccountId,
    ) -> u64 {
        let buyer = env::predecessor_account_id();
        let deposit = env::attached_deposit();

        require!(deposit > 0, "Escrow amount must be positive");
        require!(buyer != seller, "Buyer and seller must differ");
        require!(buyer != arbiter, "Buyer and arbiter must differ");
        require!(seller != arbiter, "Seller and arbiter must differ");

        let agreement_id = self.next_agreement_id;
        self.next_agreement_id = self.next_agreement_id.checked_add(1).expect("Agreement ID overflow");

        let agreement = EscrowAgreement {
            agreement_id,
            buyer: buyer.clone(),
            seller: seller.clone(),
            arbiter,
            amount: deposit,
            status: EscrowStatus::Funded,
            created_at_block: env::block_height(),
            completion_evidence_hash: None,
        };

        self.agreements.insert(&agreement_id, &agreement);
        self.total_locked_funds = self.total_locked_funds
            .checked_add(deposit)
            .expect("Total locked funds overflow");

        env::log_str(&format!(
            "{{\"event\":\"agreement_created\",\"id\":{},\"buyer\":\"{}\",\"seller\":\"{}\",\"amount\":\"{}\"}}",
            agreement_id, buyer, seller, deposit
        ));

        agreement_id
    }

    /// Seller submits evidence of completion
    pub fn submit_evidence(&mut self, agreement_id: u64, evidence_hash: String) {
        let caller = env::predecessor_account_id();
        let mut agreement = self.agreements.get(&agreement_id).expect("Agreement not found");

        require!(caller == agreement.seller, "Only seller can submit evidence");
        require!(agreement.status == EscrowStatus::Funded, "Invalid status for submission");
        require!(!evidence_hash.trim().is_empty(), "Evidence hash cannot be empty");

        agreement.evidence_hash_set(evidence_hash);
        agreement.status = EscrowStatus::WorkSubmitted;
        self.agreements.insert(&agreement_id, &agreement);
    }

    /// Release funds to seller. Allowed by Buyer (direct approval) or Arbiter (dispute resolution)
    #[payable]
    pub fn release_funds(&mut self, agreement_id: u64) -> Promise {
        assert_one_yocto(); // Require cryptographic authorization
        let caller = env::predecessor_account_id();
        let mut agreement = self.agreements.get(&agreement_id).expect("Agreement not found");

        require!(
            caller == agreement.buyer || caller == agreement.arbiter,
            "Only buyer or arbiter can release escrow funds"
        );
        require!(
            agreement.status == EscrowStatus::Funded || agreement.status == EscrowStatus::WorkSubmitted || agreement.status == EscrowStatus::Disputed,
            "Agreement not in releasable status"
        );

        let payout_amount = agreement.amount;
        let recipient = agreement.seller.clone();

        // [Checks-Effects-Interactions Pattern]: Update state to Pending Completed BEFORE promise
        agreement.status = EscrowStatus::Completed;
        self.agreements.insert(&agreement_id, &agreement);
        self.total_locked_funds = self.total_locked_funds
            .checked_sub(payout_amount)
            .expect("Locked funds underflow");

        Promise::new(recipient.clone())
            .transfer(payout_amount)
            .then(
                Self::ext(env::current_account_id())
                    .with_static_gas(GAS_FOR_RESOLVE_PAYOUT)
                    .on_release_complete(agreement_id, recipient, U128(payout_amount))
            )
    }

    /// Private callback verifying Promise execution and recovering safely if failed
    #[private]
    pub fn on_release_complete(
        &mut self,
        agreement_id: u64,
        recipient: AccountId,
        amount: U128,
    ) -> bool {
        let amount_u128: Balance = amount.into();
        match env::promise_result(0) {
            PromiseResult::Successful(_) => {
                env::log_str(&format!(
                    "{{\"event\":\"payout_success\",\"id\":{},\"recipient\":\"{}\",\"amount\":\"{}\"}}",
                    agreement_id, recipient, amount_u128
                ));
                true
            }
            PromiseResult::Failed => {
                // Secure roll-back of escrow state in event of transfer failure
                if let Some(mut agreement) = self.agreements.get(&agreement_id) {
                    agreement.status = EscrowStatus::Disputed;
                    self.agreements.insert(&agreement_id, &agreement);
                    self.total_locked_funds = self.total_locked_funds.saturating_add(amount_u128);
                }
                env::log_str(&format!(
                    "{{\"event\":\"payout_failed_recovered\",\"id\":{},\"amount\":\"{}\"}}",
                    agreement_id, amount_u128
                ));
                false
            }
        }
    }

    pub fn get_agreement(&self, agreement_id: u64) -> Option<EscrowAgreement> {
        self.agreements.get(&agreement_id)
    }

    pub fn get_total_locked(&self) -> U128 {
        U128(self.total_locked_funds)
    }
}

impl EscrowAgreement {
    pub fn evidence_hash_set(&mut self, hash: String) {
        self.completion_evidence_hash = Some(hash);
    }
}`;

export const DEFAULT_CONTRACTS: ContractSample[] = [
  {
    id: "vulnerable_vault",
    name: "VulnerableVault.rs",
    description: "High-yield DeFi vault with critical callback reentrancy, economic share price inflation, and missing emergency access controls.",
    code: VULNERABLE_VAULT_CODE,
    expected_vulnerabilities: [
      "Callback Reentrancy & Unhandled State Inconsistency",
      "Economic Flash-Deposit / Vault Share Rounding Exploit",
      "Missing Access Control in Emergency Function",
      "Storage Exhaustion / Unmetered State DoS"
    ]
  },
  {
    id: "secure_escrow",
    name: "SecureEscrow.rs",
    description: "Production-grade NEAR escrow contract implementing Checks-Effects-Interactions, safe #[private] callbacks, and NEP-145 storage bounds.",
    code: SECURE_ESCROW_CODE,
    expected_vulnerabilities: []
  }
];
