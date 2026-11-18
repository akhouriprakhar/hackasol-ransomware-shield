import React, { useEffect, useState, useRef } from 'react';

interface DecryptedTextProps {
  text: string;
  speed?: number;
  maxIterations?: number;
  characters?: string;
  className?: string;
  animateOn?: 'view' | 'change';
}

const DEFAULT_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';

export const DecryptedText: React.FC<DecryptedTextProps> = ({
  text,
  speed = 40,
  maxIterations = 10,
  characters = DEFAULT_CHARS,
  className = '',
  animateOn = 'change',
}) => {
  const [displayText, setDisplayText] = useState(text);
  const [isScrambling, setIsScrambling] = useState(false);
  const prevTextRef = useRef(text);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    let iteration = 0;

    setIsScrambling(true);

    interval = setInterval(() => {
      setDisplayText(() =>
        text
          .split('')
          .map((letter, index) => {
            if (letter === ' ') return ' ';
            if (index < Math.floor(iteration / 2)) {
              return text[index];
            }
            return characters[Math.floor(Math.random() * characters.length)];
          })
          .join('')
      );

      iteration += 1;

      if (iteration >= text.length * 2 + maxIterations) {
        setDisplayText(text);
        setIsScrambling(false);
        clearInterval(interval);
      }
    }, speed);

    prevTextRef.current = text;

    return () => clearInterval(interval);
  }, [text, speed, maxIterations, characters]);

  return (
    <span className={`font-mono transition-colors ${className}`}>
      {displayText}
    </span>
  );
};
