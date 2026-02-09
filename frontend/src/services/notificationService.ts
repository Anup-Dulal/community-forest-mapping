/**
 * Notification service for displaying success, error, and info messages.
 * Manages notification state and lifecycle.
 */

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  title?: string;
  duration?: number; // milliseconds, 0 = no auto-dismiss
  dismissible?: boolean;
}

class NotificationService {
  private notifications: Map<string, Notification> = new Map();
  private listeners: Set<(notifications: Notification[]) => void> = new Set();
  private nextId = 0;

  /**
   * Subscribe to notification changes.
   */
  subscribe(listener: (notifications: Notification[]) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners of changes.
   */
  private notifyListeners(): void {
    const notifications = Array.from(this.notifications.values());
    this.listeners.forEach((listener) => listener(notifications));
  }

  /**
   * Add a success notification.
   */
  success(message: string, title?: string, duration = 5000): string {
    return this.add({
      type: 'success',
      message,
      title,
      duration,
      dismissible: true
    });
  }

  /**
   * Add an error notification.
   */
  error(message: string, title?: string, duration = 7000): string {
    return this.add({
      type: 'error',
      message,
      title,
      duration,
      dismissible: true
    });
  }

  /**
   * Add an info notification.
   */
  info(message: string, title?: string, duration = 4000): string {
    return this.add({
      type: 'info',
      message,
      title,
      duration,
      dismissible: true
    });
  }

  /**
   * Add a warning notification.
   */
  warning(message: string, title?: string, duration = 5000): string {
    return this.add({
      type: 'warning',
      message,
      title,
      duration,
      dismissible: true
    });
  }

  /**
   * Add a custom notification.
   */
  add(notification: Omit<Notification, 'id'>): string {
    const id = `notification-${this.nextId++}`;
    const fullNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000,
      dismissible: notification.dismissible ?? true
    };

    this.notifications.set(id, fullNotification);
    this.notifyListeners();

    // Auto-dismiss if duration is set
    if (fullNotification.duration > 0) {
      setTimeout(() => this.dismiss(id), fullNotification.duration);
    }

    return id;
  }

  /**
   * Dismiss a notification by ID.
   */
  dismiss(id: string): void {
    this.notifications.delete(id);
    this.notifyListeners();
  }

  /**
   * Dismiss all notifications.
   */
  dismissAll(): void {
    this.notifications.clear();
    this.notifyListeners();
  }

  /**
   * Get all current notifications.
   */
  getAll(): Notification[] {
    return Array.from(this.notifications.values());
  }

  /**
   * Get a notification by ID.
   */
  get(id: string): Notification | undefined {
    return this.notifications.get(id);
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
