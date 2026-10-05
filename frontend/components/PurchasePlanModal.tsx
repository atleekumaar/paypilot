"use client";

import React, { useState } from "react";
import {
  X,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  Truck,
  ArrowRight,
  AlertCircle,
  Loader2,
  Receipt,
  ExternalLink,
} from "lucide-react";

interface Product {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price: number;
  currency: string;
  rating: number;
  review_count: number;
  stock: boolean;
  seller: string;
  delivery_days: number;
  features: Record<string, any>;
}

interface RankedProduct {
  product: Product;
  product_id: string;
  rank: number;
  score: number;
  match_reasons: string[];
}

interface PurchasePlan {
  id: string;
  user_id: string;
  product_id: string;
  product_name: string;
  brand: string;
  seller: string;
  delivery_days: number;
  quantity: number;
  unit_price: number;
  currency: string;
  total_amount: number;
  status: string;
  paypal_order_id?: string;
  recommendation_reason?: string;
  score?: number;
}

interface PaymentRecord {
  id: string;
  purchase_plan_id: string;
  provider: string;
  provider_order_id: string;
  amount: number;
  currency: string;
  status: string;
  capture_id?: string;
  payer_email?: string;
  payer_id?: string;
  created_at: string;
}

interface PurchasePlanModalProps {
  rankedItem: RankedProduct | null;
  onClose: () => void;
}

export default function PurchasePlanModal({
  rankedItem,
  onClose,
}: PurchasePlanModalProps) {
  const [step, setStep] = useState<
    "FORMULATING" | "AWAITING_APPROVAL" | "CREATING_ORDER" | "PAYPAL_CHECKOUT" | "CAPTURING" | "SUCCESS" | "FAILED"
  >("AWAITING_APPROVAL");

  const [plan, setPlan] = useState<PurchasePlan | null>(null);
  const [payment, setPayment] = useState<PaymentRecord | null>(null);
  const [paypalOrderId, setPaypalOrderId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initialize Purchase Plan on backend
  React.useEffect(() => {
    if (!rankedItem) return;

    const createPlanOnBackend = async () => {
      setStep("FORMULATING");
      setErrorMessage(null);
      try {
        const res = await fetch("http://127.0.0.1:8000/api/purchase-plans", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            product_id: rankedItem.product.id,
            quantity: 1,
            score: rankedItem.score,
            recommendation_reason: rankedItem.match_reasons.join("; "),
          }),
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Failed to create purchase plan");
        }

        const data: PurchasePlan = await res.json();
        setPlan(data);
        setStep("AWAITING_APPROVAL");
      } catch (err: any) {
        console.error("Plan creation error:", err);
        setErrorMessage(err.message || "Failed to formulate Purchase Plan.");
        setStep("FAILED");
      }
    };

    createPlanOnBackend();
  }, [rankedItem]);

  // Step 1: User Explicitly Approves Purchase Plan
  const handleApprovePlan = async () => {
    if (!plan) return;
    setStep("CREATING_ORDER");
    setErrorMessage(null);

    try {
      // 1. Approve plan
      const approveRes = await fetch(
        `http://127.0.0.1:8000/api/purchase-plans/${plan.id}/approve`,
        { method: "POST" }
      );
      if (!approveRes.ok) {
        const err = await approveRes.json();
        throw new Error(err.detail || "Failed to approve purchase plan");
      }
      const updatedPlan: PurchasePlan = await approveRes.json();
      setPlan(updatedPlan);

      // 2. Create PayPal Sandbox Order
      const orderRes = await fetch(
        "http://127.0.0.1:8000/api/payments/paypal/create-order",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ purchase_plan_id: updatedPlan.id }),
        }
      );
      if (!orderRes.ok) {
        const err = await orderRes.json();
        throw new Error(err.detail || "Failed to create PayPal Order");
      }

      const orderData = await orderRes.json();
      setPaypalOrderId(orderData.paypal_order_id);
      setStep("PAYPAL_CHECKOUT");
    } catch (err: any) {
      console.error("Approval error:", err);
      setErrorMessage(err.message || "Failed to initiate PayPal Checkout.");
      setStep("FAILED");
    }
  };

  // Step 2: Capture PayPal Order after buyer approval
  const handleCapturePayment = async () => {
    if (!plan || !paypalOrderId) return;
    setStep("CAPTURING");
    setErrorMessage(null);

    try {
      const captureRes = await fetch(
        "http://127.0.0.1:8000/api/payments/paypal/capture",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            purchase_plan_id: plan.id,
            paypal_order_id: paypalOrderId,
          }),
        }
      );

      if (!captureRes.ok) {
        const err = await captureRes.json();
        throw new Error(err.detail || "Payment capture failed");
      }

      const paymentData: PaymentRecord = await captureRes.json();
      setPayment(paymentData);
      setStep("SUCCESS");
    } catch (err: any) {
      console.error("Capture error:", err);
      setErrorMessage(
        err.message ||
          "Payment wasn't completed. Your Purchase Plan has not been marked as paid. You can try again."
      );
      setStep("FAILED");
    }
  };

  if (!rankedItem) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl bg-[#0b101d] border border-cyan-500/30 rounded-2xl shadow-2xl p-6 sm:p-8 overflow-hidden text-left">
        {/* Top Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* State: Formulating */}
        {step === "FORMULATING" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
            <h3 className="text-base font-semibold text-white">Formulating Purchase Plan...</h3>
            <p className="text-xs text-slate-400">Verifying live inventory and authoritative catalog pricing.</p>
          </div>
        )}

        {/* State: Awaiting Approval (Section 5) */}
        {step === "AWAITING_APPROVAL" && plan && (
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">
                  Plan #{plan.id}
                </span>
                <h3 className="text-xl font-extrabold text-white tracking-wide">PURCHASE PLAN</h3>
              </div>
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                <span>PayPal Sandbox</span>
              </div>
            </div>

            {/* Product Card Snippet */}
            <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 mb-5">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs text-slate-400 uppercase tracking-wider">{plan.brand}</span>
                  <h4 className="text-base font-bold text-white mt-0.5">{plan.product_name}</h4>
                  <p className="text-xs text-slate-400 mt-1">Sold by {plan.seller}</p>
                </div>
                {plan.score && (
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/80 border border-cyan-800/40 px-2 py-0.5 rounded-md">
                    {plan.score}/100 Match
                  </span>
                )}
              </div>
            </div>

            {/* Breakdown Table */}
            <div className="space-y-2.5 text-xs border-b border-slate-800 pb-4 mb-4 text-slate-300">
              <div className="flex justify-between">
                <span className="text-slate-400">Unit Price</span>
                <span className="font-mono text-white">
                  ${plan.unit_price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Quantity</span>
                <span className="font-mono text-white">{plan.quantity}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Estimated Delivery</span>
                <span className="text-white flex items-center gap-1">
                  <Truck className="w-3 h-3 text-cyan-400" />
                  {plan.delivery_days} business days
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Payment Method</span>
                <span className="font-semibold text-cyan-400">PayPal (Sandbox Mode)</span>
              </div>
            </div>

            {/* Why This Product */}
            <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-800/30 text-xs mb-5">
              <div className="flex items-center gap-1.5 text-cyan-400 font-semibold mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                Why this product?
              </div>
              <p className="text-slate-300 leading-relaxed">
                {plan.recommendation_reason || "Ranked top choice for your requirements and budget constraints."}
              </p>
            </div>

            {/* Total Row */}
            <div className="flex items-baseline justify-between mb-6">
              <span className="text-sm font-semibold text-slate-300">Total Purchase Amount</span>
              <div className="text-2xl font-black text-cyan-400 font-mono">
                ${plan.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                <span className="text-xs text-slate-400 font-normal ml-1">{plan.currency}</span>
              </div>
            </div>

            {/* Explicit Approval Button */}
            <button
              onClick={handleApprovePlan}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm tracking-wide shadow-lg shadow-cyan-500/25 transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Approve Purchase</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <p className="text-[11px] text-center text-slate-500 mt-2.5">
              Explicit user approval is required before initiating PayPal payment.
            </p>
          </div>
        )}

        {/* State: Creating Secure Order */}
        {step === "CREATING_ORDER" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
            <h3 className="text-base font-semibold text-white">Creating Secure PayPal Order...</h3>
            <p className="text-xs text-slate-400">Communicating with PayPal Sandbox v2 API.</p>
          </div>
        )}

        {/* State: PayPal Checkout (Section 15, 16) */}
        {step === "PAYPAL_CHECKOUT" && plan && (
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">
                  Step 2 &bull; PayPal Checkout
                </span>
                <h3 className="text-xl font-extrabold text-white">PAYPAL SANDBOX</h3>
              </div>
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                <span>Sandbox Ready</span>
              </div>
            </div>

            {/* Order Confirmation Banner */}
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 mb-5">
              <div className="flex justify-between items-baseline mb-2">
                <span className="text-xs text-slate-400">Total Authorized</span>
                <span className="text-xl font-bold font-mono text-cyan-400">
                  ${plan.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {plan.currency}
                </span>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                PayPal Order ID: <span className="text-slate-200">{paypalOrderId}</span>
              </div>
            </div>

            {/* PayPal Checkout Execution Box */}
            <div className="p-6 rounded-xl bg-[#070b14] border border-cyan-500/20 text-center space-y-4 mb-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-medium">
                <ShieldCheck className="w-4 h-4 text-cyan-400" />
                Verified PayPal Sandbox Integration
              </div>
              <p className="text-xs text-slate-300 max-w-sm mx-auto">
                Click below to complete authorization in PayPal Sandbox and capture the payment.
              </p>

              {/* PayPal Primary Action Button */}
              <button
                onClick={handleCapturePayment}
                className="w-full py-3.5 rounded-xl bg-[#ffc439] hover:bg-[#f4bb34] text-[#003087] font-extrabold text-sm tracking-wide shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Pay with</span>
                <span className="italic font-black text-base">PayPal</span>
                <span className="text-xs font-normal text-slate-700 ml-1">(Sandbox)</span>
              </button>
            </div>

            <button
              onClick={() => setStep("AWAITING_APPROVAL")}
              className="w-full text-center text-xs text-slate-500 hover:text-slate-300 py-1"
            >
              Cancel and return to Purchase Plan
            </button>
          </div>
        )}

        {/* State: Capturing Payment */}
        {step === "CAPTURING" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
            <h3 className="text-base font-semibold text-white">Verifying Payment with PayPal...</h3>
            <p className="text-xs text-slate-400">Executing authoritative server-side order capture.</p>
          </div>
        )}

        {/* State: Payment Successful (Section 20) */}
        {step === "SUCCESS" && plan && payment && (
          <div className="py-4 text-center">
            {/* Green Check Icon */}
            <div className="w-16 h-16 rounded-full bg-emerald-500/10 border-2 border-emerald-400 flex items-center justify-center mx-auto mb-4 text-emerald-400 shadow-xl shadow-emerald-500/20">
              <CheckCircle2 className="w-9 h-9" />
            </div>

            <h3 className="text-2xl font-extrabold text-white tracking-wide mb-1">
              PAYMENT SUCCESSFUL
            </h3>
            <p className="text-xs text-emerald-400 font-medium mb-6">
              Verified by PayPal Sandbox &bull; Status: {payment.status}
            </p>

            {/* Receipt Card */}
            <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-4 text-left space-y-2.5 text-xs text-slate-300 mb-6 font-mono">
              <div className="flex justify-between border-b border-slate-800 pb-2">
                <span className="text-slate-500">Item</span>
                <span className="font-semibold text-white">{plan.product_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Amount Paid</span>
                <span className="text-cyan-400 font-bold">
                  ${payment.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {payment.currency}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Payment Provider</span>
                <span className="text-white">PayPal Sandbox</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">PayPal Order ID</span>
                <span className="text-slate-200 truncate max-w-[200px]">{payment.provider_order_id}</span>
              </div>
              {payment.capture_id && (
                <div className="flex justify-between">
                  <span className="text-slate-500">Capture ID</span>
                  <span className="text-slate-200">{payment.capture_id}</span>
                </div>
              )}
              {payment.payer_email && (
                <div className="flex justify-between border-t border-slate-800 pt-2">
                  <span className="text-slate-500">Buyer Account</span>
                  <span className="text-slate-300 truncate max-w-[200px]">{payment.payer_email}</span>
                </div>
              )}
            </div>

            {/* Finish Action */}
            <button
              onClick={onClose}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm transition-all shadow-lg shadow-cyan-500/20"
            >
              Back to Shopping
            </button>
          </div>
        )}

        {/* State: Failure (Section 21) */}
        {step === "FAILED" && (
          <div className="py-6 text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
              <AlertCircle className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-white">Payment Incomplete</h3>
            <p className="text-xs text-slate-300 max-w-sm mx-auto leading-relaxed">
              {errorMessage || "Payment wasn't completed. Your Purchase Plan has not been marked as paid."}
            </p>
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl border border-slate-700 bg-slate-900 text-xs font-semibold text-slate-300 hover:bg-slate-800"
              >
                Close
              </button>
              <button
                onClick={() => setStep("AWAITING_APPROVAL")}
                className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-semibold"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
