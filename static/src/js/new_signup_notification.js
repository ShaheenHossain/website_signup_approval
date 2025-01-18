/** @odoo-module **/

import { busService } from '@web/core/bus_service';
import { registry } from '@web/core/registry';
import { notificationService } from '@web/core/notification_service';

const NotificationService = registry.category('services').get('notification');

export const NewSignupNotification = {
    async start(env) {
        const bus = await env.services.bus_service;
        bus.addEventListener('notification', (notifications) => {
            for (const notification of notifications) {
                if (notification[1].type === 'new_signup') {
                    env.services.notification.add(
                        notification[1].message,
                        { type: 'info', sticky: true }
                    );
                }
            }
        });
    },
};

// Register the notification service
registry.category('services').add('new_signup_notification', NewSignupNotification);
