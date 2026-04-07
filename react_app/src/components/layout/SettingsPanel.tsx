/**
 * SettingsPanel - Slide-over settings panel with theme, API, and version info.
 */
import { X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useEffect } from "react";

interface SettingsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            aria-hidden="true"
          />

          {/* Slide-over panel */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed top-0 right-0 bottom-0 w-full max-w-md bg-zinc-900 border-l border-white/10 z-50 flex flex-col"
            role="dialog"
            aria-modal="true"
            aria-labelledby="settings-title"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-white/10">
              <h2 id="settings-title" className="text-lg font-semibold text-white">
                Settings
              </h2>
              <button
                onClick={onClose}
                aria-label="Close settings"
                className="p-2 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-white/5 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Theme Section */}
              <section>
                <h3 className="text-sm font-medium text-white mb-3">Theme</h3>
                <div className="p-4 rounded-lg bg-zinc-800/50 border border-white/5">
                  <p className="text-sm text-zinc-400">
                    Dark theme (default) — customization coming soon.
                  </p>
                </div>
              </section>

              {/* API Configuration */}
              <section>
                <h3 className="text-sm font-medium text-white mb-3">API Configuration</h3>
                <div className="p-4 rounded-lg bg-zinc-800/50 border border-white/5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">Endpoint:</span>
                    <code className="text-xs font-mono text-blue-400 bg-zinc-900 px-2 py-1 rounded">
                      {import.meta.env.VITE_API_BASE_URL || "/api/v1"}
                    </code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">Status:</span>
                    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-400">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                      Connected
                    </span>
                  </div>
                </div>
              </section>

              {/* Version Info */}
              <section>
                <h3 className="text-sm font-medium text-white mb-3">Version</h3>
                <div className="p-4 rounded-lg bg-zinc-800/50 border border-white/5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">App:</span>
                    <span className="text-sm font-mono text-zinc-300">v0.21.6</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-400">IS 456:</span>
                    <span className="text-sm font-mono text-zinc-300">2000</span>
                  </div>
                </div>
              </section>
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-white/10">
              <p className="text-xs text-zinc-500 text-center">
                structural_engineering_lib © {new Date().getFullYear()}
              </p>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
