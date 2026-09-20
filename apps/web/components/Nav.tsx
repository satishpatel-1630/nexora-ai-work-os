"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  ["/", "Dashboard"],
  ["/projects", "Projects"],
  ["/command", "Command"],
  ["/intelligence", "Intelligence"],
  ["/approvals", "Approvals"],
  ["/settings", "Settings"],
];

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="topbar">
      <Link className="brand" href="/"><span className="brand-mark">N</span><span>NEXORA</span></Link>
      <nav>{items.map(([href, label]) => <Link className={pathname === href || (href !== "/" && pathname.startsWith(href)) ? "active" : ""} href={href} key={href}>{label}</Link>)}</nav>
      <div className="top-status"><span className="pulse" /> LOCAL CONTROL PLANE</div>
    </header>
  );
}
