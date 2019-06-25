from flask_assets import Bundle, Environment

assets = Environment()

assets.register({
    'home_css': Bundle(
        'styles/home/*.css',
        filters='cssmin',
        output='build/home.min.css',
    ),
    'user_css': Bundle(
        'styles/user/*.css',
        filters='cssmin',
        output='build/user.min.css',
    ),
    'shared_css': Bundle(
        'styles/shared/*.css',
        filters='cssmin',
        output='build/shared.min.css',
    ),
    'shared_js': Bundle(
        'scripts/shared/*.js',
        filters='jsmin',
        output='build/shared.min.js',
    ),
})
