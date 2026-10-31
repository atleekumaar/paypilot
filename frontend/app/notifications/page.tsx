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
  Loader2,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

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
      const res = await fetch(`${API_BASE_URL}/api/notifications?user_id=guest_user`);
      if (res.ok) {
        const data = await res.json();
        setNotifications(data);
      }
    } catch (err) {
      console.warn("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id: string) => {
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/notifications/${id}/read?user_id=guest_user`,
        { method: "POST" }
      );
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
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "ORDER_UPDATE":
        return <Package className="w-4 h-4 text-[#0070E0]" />;
      case "PAYMENT_COMPLETED":
        return <CreditCard className="w-4 h-4 text-emerald-600" />;
      default:
        return <MessageSquare className="w-4 h-4 text-[#003087]" />;
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="flex flex-col min-h-screen bg-[#F5F8FC]/50 text-[#14213D] text-left">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between pb-6 border-b border-slate-200 mb-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#0070E0]/20 bg-[#EAF3FF] text-[#0070E0] text-xs font-bold mb-2">
              <Bell className="w-3.5 h-3.5" />
              Proactive Commerce Updates
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-[#14213D] tracking-tight flex items-center gap-3">
              Notification Center
              {unreadCount > 0 && (
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-[#EAF3FF] border border-[#0070E0]/30 text-[#0070E0] font-bold">
                  {unreadCount} unread
                </span>
              )}
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-1">
              Real-time delivery milestones, shipment delay alerts, and payment verification events.
            </p>
          </div>

          <button
            onClick={fetchNotifications}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 shadow-xs transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-[#0070E0] mb-2" />
            <p className="text-sm font-medium">Loading notifications...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-16 px-4 rounded-3xl border border-slate-200 bg-white shadow-subtle">
            <div className="w-14 h-14 rounded-2xl bg-[#EAF3FF] text-[#0070E0] flex items-center justify-center mx-auto mb-3">
              <Bell className="w-7 h-7" />
            </div>
            <h3 className="text-base font-bold text-[#14213D] mb-1">No Notifications</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              You are all caught up! New order updates, delay notices, and payment captures will appear here.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((item) => (
              <div
                key={item.id}
                className={`p-5 rounded-2xl border transition-all flex items-start justify-between gap-4 ${
                  item.read
                    ? "border-slate-200/80 bg-white/70 text-slate-500"
                    : "border-[#0070E0]/30 bg-white text-slate-800 shadow-subtle"
                }`}
              >
                <div className="flex items-start gap-3.5">
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 border ${
                      item.read
                        ? "bg-[#F5F8FC] border-slate-200"
                        : "bg-[#EAF3FF] border-[#0070E0]/20"
                    }`}
                  >
                    {getIcon(item.type)}
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h4
                        className={`text-sm font-bold ${
                          item.read ? "text-slate-700" : "text-[#14213D]"
                        }`}
                      >
                        {item.title}
                      </h4>
                      {!item.read && (
                        <span className="w-2 h-2 rounded-full bg-[#0070E0]"></span>
                      )}
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed mb-2.5">
                      {item.message}
                    </p>

                    <div className="flex items-center gap-3 text-[11px] text-slate-400 font-medium">
                      <span>
                        {new Date(item.created_at).toLocaleString([], {
                          month: "short",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                      {item.order_id && (
                        <>
                          <span>&bull;</span>
                          <Link
                            href={`/orders/${item.order_id}`}
                            className="text-[#0070E0] hover:underline flex items-center gap-1 font-mono font-semibold"
                          >
                            <span>View Order {item.order_id}</span>
                            <ArrowRight className="w-3 h-3" />
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
                    className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-500 hover:text-[#0070E0] transition-colors shrink-0 cursor-pointer shadow-2xs"
                  >
                    <Check className="w-4 h-4" />
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
