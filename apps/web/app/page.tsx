"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, Approval, Project } from "../lib/api";

function StatusDot({ ok }: { ok: boolean }) {
  return <span className={`status-dot ${ok ? "ok" : "bad"}`} aria-label={ok ? "online" : "offline"} />;
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [health, setHealth] = useState<"checking" | "online" | "offline">("checking");
  const [ready, setReady] = useState<"checking" | "ready" | "offline">("checking");

  useEffect(() => {
    void Promise.all([api.projects(), api.approvals()])
      .then(([p, a]) => {
        setProjects(p);
        setApprovals(a);
      })
      .catch(() => undefined);
    void api.health().then(() => setHealth("online")).catch(() => setHealth("offline"));
    void api.readiness().then(() => setReady("ready")).catch(() => setReady("offline"));
  }, []);

  const pending = useMemo(() => approvals.filter((x) => x.status === "pending").length, [approvals]);
  const active = useMemo(() => projects.filter((x) => x.status === "active").length, [projects]);

  return (
    <main className="dashboard-shell">
      <section className="hero">
        <div>
          <div className="eyebrow"><span className="pulse" /> PERSONAL AI WORK OS</div>
          <h1>Command your work.<br /><span>Let NEXORA execute.</span></h1>
          <p className="hero-copy">
            Research, plan, execute, evaluate and automate complex work from one control plane.
          </p>
          <div className="hero-actions">
            <Link className="button primary" href="/projects">+ New project</Link>
            <Link className="button ghost" href="/approvals">Review approvals {pending > 0 && <b>{pending}</b>}</Link>
          </div>
        </div>
        <div className="orb-card">
          <div className="orb"><div className="orb-core">N</div></div>
          <div className="orb-label"><span>NEXORA CORE</span><strong>Foundation online</strong></div>
        </div>
      </section>

      <section className="metric-grid">
        <article className="metric-card"><span>ACTIVE PROJECTS</span><strong>{active}</strong><small>{projects.length} total projects</small></article>
        <article className="metric-card"><span>PENDING APPROVALS</span><strong>{pending}</strong><small>Human control gate</small></article>
        <article className="metric-card"><span>WORKFLOWS</span><strong>0</strong><small>Execution engine coming next</small></article>
        <article className="metric-card"><span>AI PROVIDERS</span><strong>0</strong><small>Connect providers in Phase 2</small></article>
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-head"><div><span className="eyebrow">WORKSPACE</span><h2>Recent projects</h2></div><Link href="/projects">View all →</Link></div>
          {projects.length === 0 ? (
            <div className="empty-state"><div className="empty-icon">◈</div><strong>Your workspace is empty</strong><p>Create your first project and NEXORA will organize the work here.</p><Link className="button primary small" href="/projects">Create project</Link></div>
          ) : (
            <div className="project-list">{projects.slice(0, 5).map((project) => (
              <Link className="project-row" href={`/projects/${project.id}`} key={project.id}>
                <div className="project-icon">◈</div><div className="project-info"><strong>{project.name}</strong><span>{project.description || "No description"}</span></div>
                <span className="badge">{project.status}</span><span className="arrow">→</span>
              </Link>
            ))}</div>
          )}
        </div>

        <div className="panel">
          <div className="panel-head"><div><span className="eyebrow">CONTROL PLANE</span><h2>System status</h2></div><Link href="/settings">Settings →</Link></div>
          <div className="system-list">
            <div><span><StatusDot ok={health === "online"} />API</span><b>{health}</b></div>
            <div><span><StatusDot ok={ready === "ready"} />Dependencies</span><b>{ready}</b></div>
            <div><span><StatusDot ok />Policy engine</span><b>ready</b></div>
            <div><span><StatusDot ok />Approval gate</span><b>ready</b></div>
            <div><span><StatusDot ok />Agent runtime</span><b>foundation</b></div>
          </div>
          <div className="architecture">
            <span>REQUEST</span><i>→</i><span>PLAN</span><i>→</i><span>EXECUTE</span><i>→</i><span>QA</span>
          </div>
        </div>
      </section>

      <section className="next-panel">
        <div><span className="eyebrow">NEXORA ROADMAP</span><h2>Phase 1 foundation is your control plane.</h2><p>Projects, tasks, events, approvals, policy, worker runtime and the dashboard are connected. Next comes the intelligence layer: research → task intelligence → specialist selection → prompt orchestration → model routing.</p></div>
        <Link className="button ghost" href="/settings">Inspect system →</Link>
      </section>
    </main>
  );
}
