import { KPIStats } from "@/components/dashboard/kpi-stats";
import { CaseTable } from "@/components/dashboard/case-table";
import { DocketTimeline } from "@/components/dashboard/docket-timeline";
import { DocumentsCard } from "@/components/dashboard/documents-card";
import { IntelligencePanel } from "@/components/dashboard/intelligence-panel";

export default function Home() {
  return (
    <div className="space-y-5 max-w-[1600px] mx-auto">
      <header>
        <h1 className="text-xl font-bold tracking-tight text-white">
          Welcome to LIA — <span className="text-zinc-500 font-medium">Legal Intelligence Platform</span>
        </h1>
        <p className="text-[0.8rem] text-zinc-500 mt-1 max-w-2xl">
          Monitor, analyze, and manage AI-related litigation with real-time intelligence.
        </p>
      </header>

      <KPIStats />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2 space-y-5">
          <CaseTable />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <DocketTimeline />
            <DocumentsCard />
          </div>
        </div>

        <div className="xl:col-span-1">
          <IntelligencePanel />
        </div>
      </div>
    </div>
  );
}
