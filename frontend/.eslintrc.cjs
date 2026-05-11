module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
  ],
  ignorePatterns: ["dist", ".eslintrc.cjs"],
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  settings: { react: { version: "18.3" } },
  plugins: ["react-refresh"],
  rules: {
    "react-refresh/only-export-components": "off",
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
    // PropTypes not required — project uses plain JSX without TS; add types via TS migration later
    "react/prop-types": "off",
  },
};
