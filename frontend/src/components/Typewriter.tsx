import { useTypewriter } from "../hooks/useTypewriter";

export type TypewriterProps = {
    text: string;
    speed?: number;
};

const Typewriter = ({ text, speed }: TypewriterProps) => {
    const displayText = useTypewriter(text, speed);

    return <p>{displayText}</p>;
  };

  export default Typewriter;
