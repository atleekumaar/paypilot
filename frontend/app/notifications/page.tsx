"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import {
  Bell,
  Package,
  AlertTriangle,
  CreditCard,
  MessageSquare,
  Check,
  RefreshCw,
  Clock,
  ArrowRight,
} from "lucide-react";

interface NotificationItem {
  id: string;
  user_id: string;
  order_id?: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/notifications?user_id=guest_user");
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (err) {
      console.error("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/notifications/${id}/read?user_id=guest_user`, {
        method: "POST",
      });
      if (res.ok) {
        setNotifications((prev) =>
          prev.map((n) => (n.id === id ? { ...n, read: true } : n))
        );
      }
    } catch (err) {
      console.error("Failed to mark notification read:", err);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "DELIVERY_DELAY":
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case "ORDER_UPDATE":
        return <Package className="w-4 h-4 text-cyan-400" />;
      case "PAYMENT_COMPLETED":
        return <CreditCard className="w-4 h-4 text-emerald-400" />;
      default:
        return <MessageSquare className="w-4 h-4 text-blue-400" />;
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="flex flex-col min-h-screen bg-[#07090e] text-slate-100">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between pb-6 border-b border-slate-800/80 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 text-xs font-medium mb-2">
              <Bell className="w-3.5 h-3.5" />
              Proactive Commerce Updates
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              Notification Center
              {unreadCount > 0 && (
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 font-bold">
                  {unreadCount} unread
                </span>
              )}
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Real-time delivery milestones, shipment delay alerts, and payment verification events.
            </p>
          </div>

          <button
            onClick={fetchNotifications}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900/60 hover:bg-slate-800 text-xs font-medium text-slate-300"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <Clock className="w-8 h-8 animate-spin mx-auto text-cyan-400 mb-2" />
            <p className="text-sm">Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-2xl border border-slate-800/80 bg-slate-900/20">
            <Bell className="w-12 h-12 mx-auto text-slate-600 mb-3" />
            <h3 className="text-base font-semibold text-white mb-1">No Notifications</h3>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              You are all caught up! New order updates and delay notices will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((item) => (
              <div
                key={item.id}
                className={`p-4 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                  item.read
                    ? "border-slate-800/60 bg-slate-900/20 text-slate-400"
                    : "border-cyan-500/30 bg-slate-900/60 text-slate-200 shadow-md shadow-cyan-500/5"
                }`}
              >
                <div className="flex items-start gap-3.5">
                  <div
                    className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border ${
                      item.read
                        ? "bg-slate-800/40 border-slate-700/40"
                        : "bg-cyan-500/10 border-cyan-500/30"
                    }`}
                  >
                    {getIcon(item.type)}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4
                        className={`text-sm font-bold ${
                          item.read ? "text-slate-300" : "text-white"
                        }`}
                      >
                        {item.title}
                      </h4>
                      {!item.read && (
                        <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed mb-2">{item.message}</p>

                    <div className="flex items-center gap-3 text-[11px] text-slate-500">
                      <span>{new Date(item.created_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                      {item.order_id && (
                        <>
                          <span>&bull;</span>
                          <Link
                            href={`/orders/${item.order_id}`}
                            className="text-cyan-400 hover:underline flex items-center gap-1 font-mono"
                          >
                            View Order {item.order_id}
                            <ArrowRight className="w-2.5 h-2.5" />
                          </Link>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {!item.read && (
                  <button
                    onClick={() => handleMarkAsRead(item.id)}
                    title="Mark as read"
                    className="p-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition-colors shrink-0"
                  >
                    <Check className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
