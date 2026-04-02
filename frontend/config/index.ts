import { defineConfig, type UserConfigExport } from '@tarojs/cli';
import TsconfigPathsPlugin from 'tsconfig-paths-webpack-plugin';

export default defineConfig(async (merge, { mode }) => {
  const baseConfig: UserConfigExport = {
    projectName: 'prep-keeper-frontend',
    date: '2026-3-30',
    designWidth: 750,
    deviceRatio: {
      640: 2.34 / 2,
      750: 1,
      828: 1.81 / 2
    },
    sourceRoot: 'src',
    outputRoot: 'dist',
    framework: 'react',
    compiler: {
      type: 'webpack5',
      prebundle: { enable: false }
    },
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
      },
      webpackChain(chain) {
        chain.resolve.plugin('tsconfig-paths').use(TsconfigPathsPlugin);
      }
    },
    h5: {
      publicPath: '/',
      staticDirectory: 'static',
      router: {
        mode: 'browser'
      },
      devServer: {
        host: 'localhost',
        port: 10086,
        https: false,
        hot: true,
        open: false
      },
      postcss: {
        autoprefixer: {
          enable: true,
          config: {}
        },
        cssModules: {
          enable: false,
          config: {
            namingPattern: 'module',
            generateScopedName: '[name]__[local]___[hash:base64:5]'
          }
        }
      },
      webpackChain(chain) {
        chain.resolve.plugin('tsconfig-paths').use(TsconfigPathsPlugin);
        chain.optimization.splitChunks({
          chunks: 'all',
          cacheGroups: {
            vendor: {
              name: 'chunk-vendors',
              test: /[\\/]node_modules[\\/]/,
              priority: 10,
              chunks: 'initial',
            },
            common: {
              name: 'chunk-common',
              minChunks: 2,
              priority: 5,
              chunks: 'initial',
            }
          }
        });
      }
    },
    cache: {
      enable: true
    }
  };

  if (mode === 'development') {
    return merge({}, baseConfig, {
      mini: {},
      h5: {}
    });
  }

  if (mode === 'production') {
    return merge({}, baseConfig, {
      mini: {},
      h5: {}
    });
  }

  return baseConfig;
});