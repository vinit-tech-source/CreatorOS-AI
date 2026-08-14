/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** API base URL override (e.g. http://localhost:8000/api/v1) */
  readonly VITE_API_URL?: string;
  /**
   * Development auth bypass flag.
   * Set to "true" ONLY in local development (.env.development.local).
   * Has no effect in production builds (import.meta.env.DEV === false).
   * Default: undefined (bypass disabled).
   */
  readonly VITE_DEV_AUTH_BYPASS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}
