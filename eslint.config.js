module.exports = [
  {
    files: ['src/**/*.{js,ts,tsx}'],
    languageOptions: {
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    rules: {}
  },
  {
    files: ['src/**/*.{ts,tsx}'],
    languageOptions: {
      parser: require('@typescript-eslint/parser'),
      parserOptions: {
        project: './tsconfig.json',
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    plugins: {
      '@typescript-eslint': require('@typescript-eslint/eslint-plugin')
    },
    rules: {}
  }
];
