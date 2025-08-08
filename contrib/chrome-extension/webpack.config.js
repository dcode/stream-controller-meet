const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const ZipPlugin = require('zip-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  entry: {
    background: './background.mjs',
    content_script: './content_script.mjs',
    loader: './loader.js',
  },
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [['@babel/preset-env', { targets: 'last 2 chrome versions' }]],
          },
        },
      },
    ],
  },
  optimization: {
    minimize: true,
    minimizer: [new TerserPlugin()],
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'manifest.json' },
        { from: 'lib', to: 'lib' },
        { from: 'schemas.mjs' },
        { from: 'assets/icon_128.png' },
      ],
    }),
    new ZipPlugin({
      path: path.resolve(__dirname, 'dist'),
      filename: 'google-meet-plugin.zip',
    }),
    new webpack.ContextReplacementPlugin(/.*/),
  ],
};
