const path = require('path');

module.exports = {
  mode: 'production',
  entry: './static/src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static/dist/')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  devServer: {
    contentBase: [
      path.join(__dirname, 'static'),
      path.join(__dirname, 'templates')
    ],
    compress: true,
    port: 8000
  }
};