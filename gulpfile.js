/* global require */

const gulp = require('gulp');

const lintPathsJS = [
    'network/static/js/*.js',
    'gulpfile.js'
];

const lintPathsCSS = [
    'network/static/css/*.scss',
    'network/static/css/common/*.scss',
    'network/static/css/pages/*.scss',
    'network/static/css/partials/*.scss',
    'network/static/css/*.css'
];

gulp.task('js:lint', function() {
    const eslint = require('gulp-eslint');

    return gulp.src(lintPathsJS)
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failAfterError());
});

gulp.task('css:lint', function() {
    const stylelint = require('gulp-stylelint');

    return gulp.src(lintPathsCSS)
        .pipe(stylelint({
            reporters: [{ formatter: 'string', console: true}]
        }));
});

gulp.task('assets', function() {
    const p = require('./package.json');
    const assets = p.assets;

    return gulp.src(assets, {cwd : 'node_modules/**'})
        .pipe(gulp.dest('network/static/lib'));
});

gulp.task('test', gulp.parallel('js:lint', 'css:lint'));

gulp.task('default', gulp.series('assets', 'test'));
