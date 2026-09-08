import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';

interface WelcomeProps {
  disabled: boolean;
  startButtonText: string;
  assistantName?: string;
  onStartCall: () => void;
}

export const Welcome = ({
  disabled,
  startButtonText,
  assistantName = "Jarvis",
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeProps) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <section
      ref={ref}
      inert={disabled} // Note: React 19/Next 15 supports boolean 'inert'
      className={cn(
        'bg-black fixed inset-0 mx-auto flex h-svh flex-col items-center justify-center text-center overflow-hidden',
        disabled ? 'z-10' : 'z-20'
      )}
    >
      {/* Background Effects (Iron Man Theme) */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-slate-900 via-black to-black opacity-80 z-0 pointer-events-none" />
      <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] z-0 pointer-events-none" />

      {/* Rotating HUD Rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-cyan-900/30 rounded-full animate-[spin_60s_linear_infinite] pointer-events-none z-0" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-cyan-900/20 rounded-full animate-[spin_40s_linear_infinite_reverse] pointer-events-none z-0" />

      {/* Content Container */}
      <div className="relative z-10 inline-block">
        {/* GIF Container */}
        <div className="relative">
          <img
            src="/Jarvis.gif"
            alt={assistantName}
            className="w-[800px] h-auto opacity-90 hover:opacity-100 transition-opacity duration-500"
          />
        </div>

        {/* Start Button */}
        <div className="absolute bottom-10 left-1/2 transform -translate-x-1/2 w-full max-w-xs">
          <Button
            variant="outline"
            size="lg"
            onClick={() => {
              const clickSound = new Audio("/button-click.m4a");
              clickSound.volume = 0.3;
              clickSound.play().catch(() => { });
              onStartCall();
            }}
            className="w-full bg-cyan-950/30 border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-black font-mono tracking-widest uppercase py-6 shadow-[0_0_20px_rgba(6,182,212,0.2)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)] transition-all duration-300 backdrop-blur-md"
          >
            {startButtonText}
          </Button>
        </div>
      </div>

      <footer className="fixed bottom-5 left-0 z-20 flex w-full items-center justify-center pointer-events-none">
        <div className="px-4 py-2 rounded-full border border-cyan-900/50 bg-black/50 backdrop-blur-md">
          <p className="text-cyan-700 text-[10px] uppercase tracking-[0.2em]">
            System Status: Online • <span className="text-cyan-400">Ready</span>
          </p>
        </div>
      </footer>

      {/* Corner Decorative Elements */}
      <div className="fixed top-0 left-0 w-32 h-32 border-l-2 border-t-2 border-cyan-500/20 rounded-tl-3xl pointer-events-none" />
      <div className="fixed top-0 right-0 w-32 h-32 border-r-2 border-t-2 border-cyan-500/20 rounded-tr-3xl pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-32 h-32 border-l-2 border-b-2 border-cyan-500/20 rounded-bl-3xl pointer-events-none" />
      <div className="fixed bottom-0 right-0 w-32 h-32 border-r-2 border-b-2 border-cyan-500/20 rounded-br-3xl pointer-events-none" />

    </section>
  );
};
