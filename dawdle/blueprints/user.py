from datetime import datetime

from bson.objectid import ObjectId
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user

from dawdle.forms.user import (DeleteUserForm,
                               UpdateAccountDetailsForm,
                               UpdateEmailForm,
                               UpdatePasswordForm)
from dawdle.models.user import User
from dawdle.utils import send_delete_account_email, send_verification_email

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/boards')
@login_required
def boards_GET():
    return render_template('user/boards.html')


@user_bp.route('/settings')
@login_required
def settings_GET():
    return redirect(url_for('user.settings_account_details_GET'))


@user_bp.route('/settings/account-details')
@login_required
def settings_account_details_GET():
    form = UpdateAccountDetailsForm(request.form, obj=current_user)
    return render_template('user/settings-account-details.html', form=form)


@user_bp.route('/settings/account-details', methods=['POST'])
@login_required
def settings_account_details_POST():
    form = UpdateAccountDetailsForm(request.form, obj=current_user)

    if not form.validate_on_submit():
        return render_template(
            'user/settings-account-details.html',
            form=form,
        ), 400

    if not form.update_needed():
        flash('No update needed.', 'info')
        return redirect(url_for('user.settings_account_details_POST'))

    form.populate_obj(current_user)
    current_user.last_updated = datetime.utcnow()
    current_user.save()

    flash('Your account details have been updated.', 'success')

    return redirect(url_for('user.settings_account_details_POST'))


@user_bp.route('/settings/update-email')
@login_required
def settings_update_email_GET():
    form = UpdateEmailForm(request.form, email=current_user.email)
    return render_template('user/settings-update-email.html', form=form)


@user_bp.route('/settings/update-email', methods=['POST'])
@login_required
def settings_update_email_POST():
    form = UpdateEmailForm(request.form, email=current_user.email)

    if not form.validate_on_submit():
        return render_template(
            'user/settings-update-email.html',
            form=form,
        ), 400

    if not form.update_needed():
        flash('No update needed.', 'info')
        return redirect(url_for('user.settings_update_email_POST'))

    current_user.active = False
    current_user.auth_id = ObjectId()
    current_user.email = form.email.data
    current_user.last_updated = datetime.utcnow()
    current_user.save()

    redirect_target = url_for('user.settings_update_email_POST')

    send_verification_email(current_user, redirect_target=redirect_target)

    return redirect(url_for(
        'auth.verify_resend_GET',
        email=form.email.data,
        next=redirect_target,
    ))


@user_bp.route('/settings/update-password')
@login_required
def settings_update_password_GET():
    form = UpdatePasswordForm(request.form)
    return render_template('user/settings-update-password.html', form=form)


@user_bp.route('/settings/update-password', methods=['POST'])
@login_required
def settings_update_password_POST():
    form = UpdatePasswordForm(request.form)

    if not form.validate_on_submit():
        return render_template(
            'user/settings-update-password.html',
            form=form,
        ), 400

    if not form.update_needed():
        flash('No update needed.', 'info')
        return redirect(url_for('user.settings_update_password_POST'))

    current_user.password = User.encrypt_password(form.new_password.data)
    current_user.auth_id = ObjectId()
    current_user.last_updated = datetime.utcnow()
    current_user.save()

    flash('Your password has been updated.', 'success')

    login_user(current_user)

    return redirect(url_for('user.settings_update_password_POST'))


@user_bp.route('/settings/delete-account')
@login_required
def settings_delete_account_GET():
    form = DeleteUserForm(request.form)
    return render_template('user/settings-delete-account.html', form=form)


@user_bp.route('/settings/delete-account', methods=['POST'])
@login_required
def settings_delete_account_POST():
    form = DeleteUserForm(request.form)

    if not form.validate_on_submit():
        return render_template(
            'user/settings-delete-account.html',
            form=form,
        ), 400

    send_delete_account_email(current_user)

    current_user.delete()

    flash('Your account has been deleted.', 'info')

    return redirect(url_for('home.index_GET'))
