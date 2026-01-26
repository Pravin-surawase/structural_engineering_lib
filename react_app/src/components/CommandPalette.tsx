/**
 * CommandPalette Component
 *
 * Keyboard-driven command palette using cmdk.
 * Provides quick access to all app actions.
 */
import { useEffect, useState, useCallback } from 'react';
import { Command } from 'cmdk';
import {
  Upload,
  Play,
  Box,
  Settings,
  FileDown,
  RefreshCw,
  Search,
} from 'lucide-react';
import { cn } from '../lib/utils';

export interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
  shortcut?: string;
  action: () => void;
  group?: string;
}

interface CommandPaletteProps {
  commands?: CommandItem[];
  onClose?: () => void;
  isOpen?: boolean;
  setIsOpen?: (open: boolean) => void;
}

// Default commands - override with props
const defaultCommands: CommandItem[] = [
  {
    id: 'import-csv',
    label: 'Import CSV',
    description: 'Import beam data from CSV file',
    icon: <Upload className="w-4 h-4" />,
    shortcut: '⌘I',
    group: 'Import',
    action: () => console.log('Import CSV'),
  },
  {
    id: 'load-sample',
    label: 'Load Sample Data',
    description: 'Load sample beam data for testing',
    icon: <RefreshCw className="w-4 h-4" />,
    shortcut: '⌘⇧S',
    group: 'Import',
    action: () => console.log('Load sample'),
  },
  {
    id: 'design-all',
    label: 'Design All Beams',
    description: 'Run design on all imported beams',
    icon: <Play className="w-4 h-4" />,
    shortcut: '⌘⇧D',
    group: 'Design',
    action: () => console.log('Design all'),
  },
  {
    id: 'view-3d',
    label: 'Toggle 3D View',
    description: 'Show or hide 3D visualization',
    icon: <Box className="w-4 h-4" />,
    shortcut: '⌘3',
    group: 'View',
    action: () => console.log('Toggle 3D'),
  },
  {
    id: 'export-results',
    label: 'Export Results',
    description: 'Export design results to CSV/Excel',
    icon: <FileDown className="w-4 h-4" />,
    shortcut: '⌘E',
    group: 'Export',
    action: () => console.log('Export'),
  },
  {
    id: 'settings',
    label: 'Settings',
    description: 'Open application settings',
    icon: <Settings className="w-4 h-4" />,
    shortcut: '⌘,',
    group: 'App',
    action: () => console.log('Settings'),
  },
];

export function CommandPalette({
  commands = defaultCommands,
  onClose,
  isOpen: controlledOpen,
  setIsOpen: setControlledOpen,
}: CommandPaletteProps) {
  const [internalOpen, setInternalOpen] = useState(false);
  const [search, setSearch] = useState('');

  // Use controlled or internal state
  const isOpen = controlledOpen ?? internalOpen;
  const setIsOpen = setControlledOpen ?? setInternalOpen;

  // Toggle with ⌘K or Ctrl+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setIsOpen(!isOpen);
      }

      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        onClose?.();
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [isOpen, setIsOpen, onClose]);

  // Execute command and close
  const executeCommand = useCallback(
    (command: CommandItem) => {
      command.action();
      setIsOpen(false);
      setSearch('');
      onClose?.();
    },
    [setIsOpen, onClose]
  );

  // Group commands
  const groups = commands.reduce(
    (acc, cmd) => {
      const group = cmd.group || 'General';
      if (!acc[group]) acc[group] = [];
      acc[group].push(cmd);
      return acc;
    },
    {} as Record<string, CommandItem[]>
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => {
          setIsOpen(false);
          onClose?.();
        }}
      />

      {/* Command Dialog */}
      <div className="absolute left-1/2 top-[20%] -translate-x-1/2 w-full max-w-xl">
        <Command
          className={cn(
            'rounded-xl border border-zinc-700/50 bg-zinc-900/95 backdrop-blur-xl shadow-2xl overflow-hidden',
            'animate-in fade-in-0 zoom-in-95 duration-150'
          )}
          loop
        >
          {/* Search Input */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-zinc-800">
            <Search className="w-4 h-4 text-zinc-500" />
            <Command.Input
              value={search}
              onValueChange={setSearch}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent text-zinc-100 placeholder:text-zinc-500 outline-none text-sm"
            />
            <kbd className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 text-xs rounded bg-zinc-800 text-zinc-500 font-mono">
              ESC
            </kbd>
          </div>

          {/* Command List */}
          <Command.List className="max-h-[400px] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-zinc-500">
              No commands found.
            </Command.Empty>

            {Object.entries(groups).map(([groupName, groupCommands]) => (
              <Command.Group
                key={groupName}
                heading={groupName}
                className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-zinc-500"
              >
                {groupCommands.map((cmd) => (
                  <Command.Item
                    key={cmd.id}
                    value={`${cmd.label} ${cmd.description || ''}`}
                    onSelect={() => executeCommand(cmd)}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
                      'text-zinc-300 hover:bg-zinc-800/50',
                      'aria-selected:bg-zinc-800 aria-selected:text-zinc-100',
                      'transition-colors'
                    )}
                  >
                    <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-zinc-800/50">
                      {cmd.icon}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{cmd.label}</p>
                      {cmd.description && (
                        <p className="text-xs text-zinc-500 truncate">{cmd.description}</p>
                      )}
                    </div>
                    {cmd.shortcut && (
                      <kbd className="hidden sm:flex items-center gap-0.5 px-1.5 py-0.5 text-xs rounded bg-zinc-800 text-zinc-500 font-mono">
                        {cmd.shortcut}
                      </kbd>
                    )}
                  </Command.Item>
                ))}
              </Command.Group>
            ))}
          </Command.List>

          {/* Footer hint */}
          <div className="flex items-center justify-between px-4 py-2 border-t border-zinc-800 text-xs text-zinc-500">
            <span>Use ↑↓ to navigate</span>
            <span>Press ↵ to select</span>
          </div>
        </Command>
      </div>
    </div>
  );
}

/**
 * Hook for command palette with custom commands.
 */
export function useCommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [commands, setCommands] = useState<CommandItem[]>(defaultCommands);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((prev) => !prev), []);

  const addCommand = useCallback((cmd: CommandItem) => {
    setCommands((prev) => [...prev.filter((c) => c.id !== cmd.id), cmd]);
  }, []);

  const removeCommand = useCallback((id: string) => {
    setCommands((prev) => prev.filter((c) => c.id !== id));
  }, []);

  return {
    isOpen,
    setIsOpen,
    open,
    close,
    toggle,
    commands,
    setCommands,
    addCommand,
    removeCommand,
  };
}

export default CommandPalette;
