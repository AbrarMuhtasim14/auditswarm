import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NEAR Audit Swarm | Multi-Agent Adversarial Security Protocol",
  description: "Autonomous multi-agent adversarial debate graph for NEAR smart contract audits with automated on-chain testnet bounty settlement.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full antialiased">
      <body className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
