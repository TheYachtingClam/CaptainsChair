import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, /api (including the WebSocket) is proxied to the Python server (REQ-OPS-02).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://localhost:8000", ws: true },
    },
  },
});
