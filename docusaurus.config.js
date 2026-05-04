// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'LeapFrog DocWeaver Pipeline SDK',
  tagline: 'Extract structured data from documents with AI-powered pipelines',
  favicon: 'img/logo.png',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://LeapFrogRnd.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/leap-doc-weaver-sdk-docs/',

  // GitHub pages deployment config.
  organizationName: 'LeapFrogRnd', // Usually your GitHub org/user name.
  projectName: 'leap-doc-weaver-sdk-docs', // Usually your repo name.
  trailingSlash: false,

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/LeapFrogRnd/LeapX/tree/main/',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/leapx-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'LeapFrog DocWeaver Pipeline SDK',
        logo: {
          alt: 'LeapFrog DocWeaver Pipeline SDK Logo',
          src: 'img/logo.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Docs',
          },
         
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/docs/getting-started/intro',
              },
              {
                label: 'Concepts',
                to: '/docs/concepts/pipeline-overview',
              },
              {
                label: 'Guides',
                to: '/docs/guides/linear-pipeline',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'Leapfrog DocWeaver Demo',
                href: 'https://demo.docweaver.lftechnology.com/',
              },
              {
                label: 'Leapfrog',
                href: 'https://www.lftechnology.com/',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} LeapFrog DocWeaver.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
