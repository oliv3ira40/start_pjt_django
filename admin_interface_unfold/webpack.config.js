const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

// Alterne entre true e false, para minificar ou não no watch
// true: minifica no "npm run watch"
// false: não minifica no "npm run watch"
const shouldMinifyInWatch = true;

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    entry: {
      admin_interface: [
        './static/src/js/_main.js', // Arquivo de entrada do JS
        './static/src/scss/_main.scss' // Arquivo de entrada do SCSS
      ],
    },
    output: {
      filename: 'js/[name].min.js',
      path: path.resolve(__dirname, 'static'),
    },
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          }
        },
        {
          test: /\.scss$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            'sass-loader'
          ]
        },
        {
          test: /\.(png|jpg|gif|svg)$/,
          type: 'asset/resource',
          generator: {
            filename: 'images/[name].[contenthash][ext]'
          }
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: 'css/[name].min.css'
      })
    ],
    optimization: {
      minimize: isProduction || shouldMinifyInWatch, // Minifica no watch apenas se shouldMinifyInWatch for true
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: true,
            mangle: true
          },
          extractComments: isProduction ? false : true, // Remove comentários no JS apenas em produção
        }),
        new CssMinimizerPlugin({
          minimizerOptions: {
            preset: [
              'default',
              {
                discardComments: { removeAll: isProduction }, // Remove comentários no CSS apenas em produção
              },
            ],
          },
        }),
      ],
    },
    devtool: isProduction ? false : 'source-map',
    watchOptions: {
      ignored: /node_modules/,
      aggregateTimeout: 300,
      poll: 1000
    }
  };
};
