const purgecss = require('@fullhuman/postcss-purgecss');

module.exports = {
  plugins: [
    purgecss({
      content: [
        './layouts/**/*.html',
        './themes/ananke/layouts/**/*.html',
        './content/**/*.md',
      ],
      safelist: {
        // Keep dynamic classes added by Hugo/JS at runtime
        standard: [
          /^is-/,
          /^has-/,
          /^development/,
          /^production/,
          /^bg-/,          // background classes used in inline styles via params
          /^cover/,
          /^db$/,
          /^dn$/,
        ],
        // Keep all responsive suffixes (-ns, -m, -l) for any kept class
        greedy: [/\-ns$/, /\-m$/, /\-l$/],
      },
    }),
  ],
};
