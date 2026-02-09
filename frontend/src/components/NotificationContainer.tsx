import React, { useEffect, useState } from 'react';
import { notificationService, Notification } from '../services/notificationService';
import '../styles/NotificationContainer.css';

/**
 * NotificationContainer displays all active notifications.
 * Manages notification lifecycle and user interactions.
 */
export const NotificationContainer: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    // Subscribe to notification changes
    const unsubscribe = notificationService.subscribe((newNotifications) => {
      setNotifications(newNotifications);
    });

    return () => unsubscribe();
  }, []);

  const handleDismiss = (id: string) => {
    notificationService.dismiss(id);
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`notification notification-${notification.type}`}
          role="alert"
        >
          <div className="notification-content">
            {notification.title && (
              <h4 className="notification-title">{notification.title}</h4>
            )}
            <p className="notification-message">{notification.message}</p>
          </div>

          {notification.dismissible && (
            <button
              className="notification-close"
              onClick={() => handleDismiss(notification.id)}
              aria-label="Close notification"
            >
              ×
            </button>
          )}
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;
