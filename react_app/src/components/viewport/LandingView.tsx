/**
 * LandingView - Hero landing page with quick actions.
 *
 * Modern construction-themed hero with sample CSV loading.
 */
import { FileUp, Zap, Play, Download, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface LandingViewProps {
  onLoadSample: () => void;
  onImportCSV: () => void;
  onManualDesign: () => void;
  isLoading?: boolean;
}

export function LandingView({
  onLoadSample,
  onImportCSV,
  onManualDesign,
  isLoading = false,
}: LandingViewProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-8 text-center">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl"
      >
        {/* Logo/Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="mb-8 mx-auto w-24 h-24 rounded-3xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center"
        >
          <svg
            className="w-12 h-12 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
            />
          </svg>
        </motion.div>

        {/* Title */}
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-4 tracking-tight">
          Structural Engineering
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            Made Simple
          </span>
        </h1>

        {/* Subtitle */}
        <p className="text-lg md:text-xl text-white/60 mb-12 max-w-2xl mx-auto">
          Professional beam design and detailing with live 3D visualization.
          Import from ETABS, design with IS 456, export to DXF.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          {/* Primary: Load Sample */}
          <motion.button
            whileHover={{ scale: isLoading ? 1 : 1.05 }}
            whileTap={{ scale: isLoading ? 1 : 0.95 }}
            onClick={onLoadSample}
            disabled={isLoading}
            className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl shadow-lg shadow-blue-500/50 hover:shadow-xl hover:shadow-blue-500/60 transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-wait"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Loading Sample...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Try Sample Building (80 beams)
              </>
            )}
          </motion.button>

          {/* Secondary: Import */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onImportCSV}
            className="px-8 py-4 bg-white/10 text-white font-semibold rounded-xl border border-white/20 hover:bg-white/15 transition-all flex items-center justify-center gap-2"
          >
            <FileUp className="w-5 h-5" />
            Import Your CSV
          </motion.button>

          {/* Tertiary: Manual */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onManualDesign}
            className="px-8 py-4 bg-white/5 text-white/80 font-semibold rounded-xl border border-white/10 hover:bg-white/10 transition-all flex items-center justify-center gap-2"
          >
            <Play className="w-5 h-5" />
            Manual Design
          </motion.button>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <FeatureCard
            icon={<FileUp className="w-6 h-6" />}
            title="Multi-Format Import"
            description="ETABS, SAFE, STAAD Pro, Generic CSV"
          />
          <FeatureCard
            icon={
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
                />
              </svg>
            }
            title="Live 3D Preview"
            description="CAD-quality visualization with rebars"
          />
          <FeatureCard
            icon={<Download className="w-6 h-6" />}
            title="Export Ready"
            description="DXF drawings, BBS, PDF reports"
          />
        </div>
      </motion.div>

      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-30">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/20 to-transparent rounded-full blur-3xl" />
      </div>
    </div>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm"
    >
      <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-blue-400 mb-4">
        {icon}
      </div>
      <h3 className="text-white font-semibold mb-2">{title}</h3>
      <p className="text-white/50 text-sm">{description}</p>
    </motion.div>
  );
}
