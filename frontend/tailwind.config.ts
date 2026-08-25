import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        steel: "#eef2f6",
        signal: "#1f7a5a",
        amber: "#b76e00"
      }
    }
  },
  plugins: []
};

export default config;
