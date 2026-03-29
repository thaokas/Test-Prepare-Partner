const config = {
  projectName: 'prep-keeper-frontend',
  date: '2026-3-29',
  designWidth: 750,
  deviceRatio: {
    640: 2.34 / 2,
    750: 1,
    828: 1.81 / 2
  },
  sourceRoot: 'src',
  outputRoot: 'dist',
  framework: 'react',
  plugins: [],
  defines: {
    __DEV__: process.env.NODE_ENV === 'development'
  },
  alias: {
    '@': 'src',
    '@components': 'src/components',
    '@pages': 'src/pages',
    '@services': 'src/services',
    '@store': 'src/store',
    '@utils': 'src/utils',
    '@types': 'src/types'
  },
  sass: {
    data: `@import "@/styles/variables.scss";`
  },
  mini: {
    postcss: {
      pxtransform: {
        enable: true,
        config: {
          selectorBlackList: ['.van-']
        }
      },
      cssModules: {
        enable: false,
        config: {
          namingPattern: 'module',
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    }
  },
  h5: {
    publicPath: '/',
    staticDirectory: 'static',
    postcss: {
      autoprefixer: {
        enable: true,
        config: {
          browsers: ['last 3 versions', 'Android >= 4.1', 'ios >= 8']
        }
      },
      cssModules: {
        enable: false,
        config: {
          namingPattern: 'module',
          generateScopedName: '[name]__[local]___[hash:base64:5]'
        }
      }
    },
    devServer: {
      host: 'localhost',
      port: 10086,
      https: false
    },
    router: {
      mode: 'browser'
    }
  },
  rn: {
    appName: 'prepKeeper',
    postcss: {
      cssModules: {
        enable: false
      }
    }
  }
}

module.exports = function (
  merge: (
    target: Record<string, any>,
    ...sources: Record<string, any>[]
  ) => Record<string, any>,
) {
  if (process.env.NODE_ENV === "development") {
    return merge({}, config, require("./dev"));
  }
  return merge({}, config, require("./prod"));
};