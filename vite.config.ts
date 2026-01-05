import path from "node:path"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"

// https://vitejs.dev/config/
export default defineConfig({
  base: "/app/",
  root: ".",
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./octobot_node/ui/src"),
    },
  },
  build: {
    outDir: "octobot_node/ui/dist",
    emptyOutDir: true,
  },
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
      routesDirectory: "./octobot_node/ui/src/routes",
      generatedRouteTree: "./octobot_node/ui/src/routeTree.gen.ts",
    }),
    react(),
    tailwindcss(),
  ],
})
