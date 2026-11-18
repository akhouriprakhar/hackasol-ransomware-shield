import React from 'react';

interface MarqueeProps {
  children: React.ReactNode;
  direction?: 'left' | 'right';
  pauseOnHover?: boolean;
  speed?: number; // duration in seconds
  className?: string;
}

export const Marquee: React.FC<MarqueeProps> = ({
  children,
  direction = 'left',
  pauseOnHover = true,
  speed = 35,
  className = '',
}) => {
  return (
    <div
      className={`relative w-full overflow-hidden flex [mask-image:linear-gradient(to_right,transparent,black_10%,black_90%,transparent)] ${className}`}
      style={{ '--marquee-duration': `${speed}s` } as React.CSSProperties}
    >
      <div
        className={`flex shrink-0 items-center justify-around gap-6 animate-marquee ${
          pauseOnHover ? 'hover:[animation-play-state:paused]' : ''
        }`}
      >
        {children}
      </div>
      <div
        aria-hidden="true"
        className={`flex shrink-0 items-center justify-around gap-6 animate-marquee ${
          pauseOnHover ? 'hover:[animation-play-state:paused]' : ''
        }`}
      >
        {children}
      </div>
    </div>
  );
};
