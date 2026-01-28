/**
 * ModeSelectPage - Choose between Manual Beam Design and Batch Import.
 */
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Box, Building2, ArrowLeft } from "lucide-react";

interface ModeCardProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  description: string;
  onClick: () => void;
  delay: number;
  gradient: string;
}

function ModeCard({ icon, title, subtitle, description, onClick, delay, gradient }: ModeCardProps) {
  return (
    <motion.button
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ y: -8, scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="group relative flex flex-col items-center text-center p-10 rounded-3xl bg-white/[0.03] border border-white/10 hover:border-white/20 hover:bg-white/[0.06] transition-all duration-300 w-full max-w-sm"
    >
      {/* Glow effect on hover */}
      <div className={`absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${gradient} blur-xl -z-10`} />

      {/* Icon */}
      <div className="w-16 h-16 rounded-2xl bg-white/5 group-hover:bg-white/10 flex items-center justify-center mb-6 transition-colors">
        {icon}
      </div>

      {/* Title */}
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>

      {/* Subtitle */}
      <p className="text-sm text-white/50 mb-4">{subtitle}</p>

      {/* Description */}
      <p className="text-xs text-white/30 leading-relaxed">{description}</p>

      {/* Arrow indicator */}
      <div className="mt-6 px-4 py-2 rounded-xl bg-white/5 group-hover:bg-white/10 text-sm text-white/50 group-hover:text-white/80 transition-all">
        Get Started →
      </div>
    </motion.button>
  );
}

export function ModeSelectPage() {
  const navigate = useNavigate();

  return (
    <div className="h-screen w-screen bg-zinc-950 flex flex-col items-center justify-center px-6 pt-14">
      {/* Back button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        onClick={() => navigate("/")}
        className="absolute top-20 left-6 p-2 rounded-lg text-white/40 hover:text-white/70 hover:bg-white/5 transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
      </motion.button>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center mb-12"
      >
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
          What would you like to do?
        </h1>
        <p className="text-white/40">Choose your workflow</p>
      </motion.div>

      {/* Cards */}
      <div className="flex flex-col md:flex-row gap-8 items-center">
        <ModeCard
          icon={<Box className="w-8 h-8 text-blue-400" />}
          title="Design a Beam"
          subtitle="Manual input with live 3D preview"
          description="Enter dimensions, materials, and forces. See real-time 3D visualization with rebar detailing and IS 456 compliance."
          onClick={() => navigate("/design")}
          delay={0.3}
          gradient="bg-blue-500/10"
        />

        <ModeCard
          icon={<Building2 className="w-8 h-8 text-purple-400" />}
          title="Batch Design"
          subtitle="Import from ETABS / SAFE / STAAD"
          description="Upload geometry and forces CSVs. Preview, design all beams at once, and explore results in the building editor."
          onClick={() => navigate("/import")}
          delay={0.45}
          gradient="bg-purple-500/10"
        />
      </div>

      {/* Quick sample link */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-12 text-sm text-white/30"
      >
        No data?{" "}
        <button
          onClick={() => navigate("/import")}
          className="text-blue-400/60 hover:text-blue-400 underline underline-offset-2 transition-colors"
        >
          Try our sample building (154 beams)
        </button>
      </motion.p>
    </div>
  );
}
