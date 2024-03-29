from flask_assets import Bundle, Environment

assets = Environment()

assets.register({
    'dawdle_css': Bundle(
        'styles/**/*.css',
        filters='cssmin',
        output='build/dawdle.min.css',
    ),
    'dawdle_js': Bundle(
        'scripts/**/*.js',
        filters='jsmin',
        output='build/dawdle.min.js',
    ),
})
