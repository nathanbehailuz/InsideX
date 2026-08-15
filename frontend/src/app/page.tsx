import Link from "next/link";
import Image from "next/image";
import {
  ArrowRightIcon,
  FileTextIcon,
  BrainCircuitIcon,
  BarChart3Icon,
} from "lucide-react";
import { Navigation, SiteFooter } from "@/components/layout/Navigation";

const POSITIONING =
  "An AI platform that analyzes financial disclosures and transactions from influential decision-makers to identify market signals.";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-on-surface flex flex-col relative overflow-x-hidden">
      <div className="ambient-glow" />
      <Navigation />

      <main className="flex-grow pt-24 pb-16 relative z-10 os-container w-full">
        <section className="py-16 md:py-20 flex flex-col items-center text-center max-w-[800px] mx-auto">
          <Image
            src="/opensignal-logo.png"
            alt="OpenSignal"
            width={64}
            height={64}
            className="h-16 w-16 mx-auto rounded-lg shadow-sm border border-border mb-6"
            priority
          />
          <h1 className="text-4xl md:text-[56px] md:leading-[64px] font-bold text-on-surface mb-4 tracking-tight">
            OpenSignal
          </h1>
          <p className="text-base md:text-lg text-on-surface-variant max-w-[600px] mx-auto mb-10">
            {POSITIONING}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-center w-full sm:w-auto">
            <Link
              href="/dashboard"
              className="os-btn-primary inline-flex items-center gap-2 w-full sm:w-auto justify-center"
            >
              View Signals Dashboard
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
            <Link
              href="/signals"
              className="os-btn-secondary inline-flex items-center justify-center w-full sm:w-auto"
            >
              Explore Market Signals
            </Link>
          </div>
        </section>

        <section className="py-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: FileTextIcon,
              title: "Disclosure Tracking",
              body: "Monitor thousands of regulatory filings in real-time. Our system automatically parses complex documents to extract actionable intelligence before it reaches mainstream news.",
            },
            {
              icon: BrainCircuitIcon,
              title: "AI-Powered Signals",
              body: "Advanced machine learning models evaluate transaction contexts, historical success rates, and unusual volume to highlight high-confidence trading signals.",
            },
            {
              icon: BarChart3Icon,
              title: "Smart Rankings",
              body: "Evaluate executives and firms based on their historical trading accuracy. We score decision-makers to help you follow the smart money with proven track records.",
            },
          ].map(({ icon: Icon, title, body }) => (
            <div
              key={title}
              className="os-card p-6 relative overflow-hidden group hover:shadow-[0_8px_16px_rgba(0,0,0,0.08)] transition-shadow"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-primary-container opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="h-12 w-12 rounded bg-surface-container flex items-center justify-center mb-4 text-primary-container">
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-on-surface mb-2">{title}</h3>
              <p className="text-sm text-on-surface-variant leading-relaxed">{body}</p>
            </div>
          ))}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
