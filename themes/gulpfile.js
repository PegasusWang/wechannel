var gulp = require('gulp');
var glob = require("glob");
var path = require("path");
var os = require("os");
var webpack = require('webpack-stream');
var autoprefixer = require('autoprefixer');
var precss = require('precss');
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var browserSync = require('browser-sync');
var reload = browserSync.reload;
var plumber = require('gulp-plumber')


var appRoot = __dirname;
var viewRoot = path.join(__dirname, '/views');
var nodeRoot = path.join(__dirname, '/node_modules');

/* 开发任务 */
gulp.task('webpack', function () {

    // 自动获取entrys
    var entries = {};

    var entryFiles = glob.sync('./views/**/*.entry.coffee');

    for(var i = 0; i < entryFiles.length; i++) {
        var filePath = entryFiles[i];
        key = '.' + filePath.substring(7, filePath.lastIndexOf('.'));
        entries[key] = path.join(__dirname, filePath);
    }

    console.log(os.hostname());
    console.log(path.join(__dirname, '/static'))

    return webpack({
        // 开发环境下监视文件改动，实时重新打包
        watch: true,
        // 入口配置
        entry: entries,
        // 输出配置
        output: {
            publicPath: 'http://127.0.0.1:8888/static/',
            filename: '[name].js'
        },
        // 模块配置
        module: {
            // 加载器
            loaders: [
                { test: /\.js$/, loader: 'babel-loader' },
                { test: /\.coffee$/, loader: 'coffee-loader'},
                { test: /\.css$/, loader: 'style-loader!css-loader!postcss-loader?pack=cleaner' },
                { test: /\.scss$/, loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader!postcss-loader?pack=cleaner') },
                { test: /\.(png|jpg|gif)$/, loader: 'file-loader?name=lib/assets/[hash].[ext]'},
                { test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: 'url-loader?limit=10000&minetype=application/font-woff&name=lib/assets/[hash].[ext]' },
                { test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/, loader: 'file-loader?name=lib/assets/[hash].[ext]' },
            ]
        },
        // css预处理
        postcss: function () {
            return {
                defaults: [autoprefixer, precss],
                cleaner:  [autoprefixer({ browsers: ['> 1% in CN'] })]
            };
        },
        externals: {
            'jquery':'jQuery'
        },
        resolve: {
            root: [appRoot, nodeRoot],
            modulesDirectories: [nodeRoot, viewRoot]
        },
        plugins: [
            new ExtractTextPlugin('[name].css')
        ],
        stats: {
            children: false
        }
    })
    .on('error', function handleError() {
        this.emit('end'); // Recover from errors
    })
    .pipe(gulp.dest('./assets'))    // gulp 输出路径
});


gulp.task('serve', function() {
    browserSync.init({
        proxy: 'localhost:8888',    // use proxy mode
    });
    gulp.watch([
        'views/**/*.html',
        'views/**/*.coffee',
        'views/**/*.scss',
        'views/**/*.css',
        'views/**/*.js',
    ]).on('change', reload);
});


gulp.task('default', ['webpack', 'serve'], function () {});
