import Link from "next/link";
import { TrendingUpIcon, ArrowRightIcon, ActivityIcon, BrainIcon } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">IX</span>
            </div>
            <span className="text-xl font-bold text-gray-900">InsideX</span>
          </div>
          <Link
            href="/dashboard"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Turn Insider Trading
            <span className="block text-blue-600">Into Smart Trades</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Ever wonder what CEOs and company executives know that we don&apos;t? Spoiler: a lot. 
            When they start buying boatloads of their own company&apos;s stock, it&apos;s usually a hint 
            that something good is about to happen.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              href="/dashboard"
              className="inline-flex items-center px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              <TrendingUpIcon className="h-5 w-5 mr-2" />
              View Signals Dashboard
              <ArrowRightIcon className="h-5 w-5 ml-2" />
            </Link>
            <Link
              href="/signals"
              className="inline-flex items-center px-8 py-4 border-2 border-blue-600 text-blue-600 text-lg font-semibold rounded-lg hover:bg-blue-50 transition-colors"
            >
              <ActivityIcon className="h-5 w-5 mr-2" />
              Explore Insider Activity
            </Link>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mt-20">
            <div className="bg-white p-8 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <ActivityIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Real-Time Data</h3>
              <p className="text-gray-600">
                Track SEC Form 4 filings in real-time and get alerts on significant insider trading activity.
              </p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <BrainIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">AI-Powered Signals</h3>
              <p className="text-gray-600">
                Machine learning models analyze historical patterns to predict which insider trades signal potential opportunities.
              </p>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <TrendingUpIcon className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Smart Rankings</h3>
              <p className="text-gray-600">
                Get ranked trading signals based on insider role, trade size, timing, and historical performance.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500">
          <p>&copy; 2025 InsideX. Built for educational and research purposes.</p>
          <p className="mt-2 text-sm">
            All insider trading data sourced from public SEC filings. Not investment advice.
          </p>
        </div>
      </footer>
    </div>
  );
}