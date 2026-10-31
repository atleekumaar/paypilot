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
  ExternalLink,
} from "lucide-react";
import { api } from "@/lib/api";

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
  approval_url?: string;
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
  const [approvalUrl, setApprovalUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initialize Purchase Plan on backend
  React.useEffect(() => {
    if (!rankedItem) return;

    const createPlanOnBackend = async () => {
      setStep("FORMULATING");
      setErrorMessage(null);
      try {
        const data: PurchasePlan = await api.post("/api/purchase-plans", {
          product_id: rankedItem.product.id,
          quantity: 1,
          score: rankedItem.score,
          recommendation_reason: rankedItem.match_reasons.join("; "),
        });
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
      const updatedPlan: PurchasePlan = await api.post(
        `/api/purchase-plans/${plan.id}/approve`
      );
      setPlan(updatedPlan);

      const orderData: any = await api.post(
        "/api/payments/paypal/create-order",
        { purchase_plan_id: updatedPlan.id }
      );

      setPaypalOrderId(orderData.paypal_order_id);
      setApprovalUrl(orderData.approval_url || null);
      setStep("PAYPAL_CHECKOUT");
    } catch (err: any) {
      console.error("Approval error:", err);
      setErrorMessage(err.message || "Failed to initiate PayPal Checkout.");
      setStep("FAILED");
    }
  };

  // Step 2: Capture PayPal Order
  const handleCapturePayment = async () => {
    if (!plan || !paypalOrderId) return;
    setStep("CAPTURING");
    setErrorMessage(null);

    try {
      const paymentData: PaymentRecord = await api.post(
        "/api/payments/paypal/capture",
        {
          purchase_plan_id: plan.id,
          paypal_order_id: paypalOrderId,
        }
      );
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-200 text-left">
      <div className="relative w-full max-w-xl bg-white border border-slate-200 rounded-3xl shadow-modal p-6 sm:p-8 overflow-hidden">
        {/* Top Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          aria-label="Close dialog"
        >
          <X className="w-5 h-5" />
        </button>

        {/* State: Formulating */}
        {step === "FORMULATING" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-[#0070E0] animate-spin mx-auto" />
            <h3 className="text-base font-bold text-[#14213D]">
              Formulating Purchase Plan...
            </h3>
            <p className="text-xs text-slate-500">
              Verifying real-time inventory, pricing, and authorization policies.
            </p>
          </div>
        )}

        {/* State: Awaiting Approval */}
        {step === "AWAITING_APPROVAL" && plan && (
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#0070E0] font-bold">
                  Plan #{plan.id.substring(0, 12)}
                </span>
                <h3 className="text-xl font-extrabold text-[#14213D] tracking-tight">
                  Purchase Plan
                </h3>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#EAF3FF] border border-[#0070E0]/20 text-[#0070E0] text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-[#0070E0]"></span>
                <span>PayPal Sandbox</span>
              </div>
            </div>

            {/* Product Card Snippet */}
            <div className="p-4 rounded-2xl bg-[#F5F8FC] border border-slate-200/80 mb-5">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold">
                    {plan.brand}
                  </span>
                  <h4 className="text-base font-bold text-[#14213D] mt-0.5">
                    {plan.product_name}
                  </h4>
                  <p className="text-xs text-slate-500 mt-1">
                    Fulfilled by <span className="font-medium text-slate-700">{plan.seller}</span>
                  </p>
                </div>
                {plan.score && (
                  <span className="text-xs font-mono font-bold text-[#0070E0] bg-[#EAF3FF] border border-[#0070E0]/30 px-2 py-0.5 rounded-md">
                    {plan.score}/100 Match
                  </span>
                )}
              </div>
            </div>

            {/* Breakdown Table */}
            <div className="space-y-2.5 text-xs border-b border-slate-100 pb-4 mb-4 text-slate-600">
              <div className="flex justify-between">
                <span>Unit Price</span>
                <span className="font-mono text-slate-900 font-semibold">
                  ${plan.unit_price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Quantity</span>
                <span className="font-mono text-slate-900 font-semibold">{plan.quantity}</span>
              </div>
              <div className="flex justify-between">
                <span>Estimated Delivery</span>
                <span className="text-slate-900 font-semibold flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5 text-[#0070E0]" />
                  {plan.delivery_days} business days
                </span>
              </div>
              <div className="flex justify-between">
                <span>Payment Method</span>
                <span className="font-bold text-[#003087]">PayPal (Sandbox Mode)</span>
              </div>
            </div>

            {/* Why This Product */}
            <div className="p-3.5 rounded-xl bg-[#EAF3FF]/60 border border-[#0070E0]/20 text-xs mb-5">
              <div className="flex items-center gap-1.5 text-[#0070E0] font-bold mb-1">
                <Sparkles className="w-3.5 h-3.5" />
                Why this product?
              </div>
              <p className="text-slate-700 leading-relaxed">
                {plan.recommendation_reason ||
                  "Ranked top choice matching your requested budget and specifications."}
              </p>
            </div>

            {/* Total Row */}
            <div className="flex items-baseline justify-between mb-6">
              <span className="text-sm font-bold text-slate-700">Total Purchase Amount</span>
              <div className="text-2xl font-black text-[#003087] font-mono">
                ${plan.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                <span className="text-xs text-slate-500 font-sans font-medium ml-1">
                  {plan.currency}
                </span>
              </div>
            </div>

            {/* Explicit Approval Button */}
            <button
              onClick={handleApprovePlan}
              className="w-full py-3.5 rounded-2xl bg-[#0070E0] hover:bg-[#005bb5] text-white font-bold text-sm tracking-wide shadow-sm hover:shadow transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <span>Approve Purchase</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <p className="text-[11px] text-center text-slate-400 mt-2.5">
              Explicit human approval is required before initiating PayPal checkout.
            </p>
          </div>
        )}

        {/* State: Creating Secure Order */}
        {step === "CREATING_ORDER" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-[#0070E0] animate-spin mx-auto" />
            <h3 className="text-base font-bold text-[#14213D]">
              Creating Secure PayPal Order...
            </h3>
            <p className="text-xs text-slate-500">
              Communicating with PayPal Sandbox v2 API.
            </p>
          </div>
        )}

        {/* State: PayPal Checkout */}
        {step === "PAYPAL_CHECKOUT" && plan && (
          <div>
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-[#0070E0] font-bold">
                  Step 2 &bull; PayPal Checkout
                </span>
                <h3 className="text-xl font-black text-[#003087]">
                  PayPal <span className="font-normal text-slate-500 text-sm">Sandbox</span>
                </h3>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span>Sandbox Ready</span>
              </div>
            </div>

            {/* Order Confirmation Banner */}
            <div className="p-4 rounded-2xl bg-[#F5F8FC] border border-slate-200 mb-5">
              <div className="flex justify-between items-baseline mb-1">
                <span className="text-xs font-medium text-slate-500">Authorized Total</span>
                <span className="text-xl font-black font-mono text-[#003087]">
                  ${plan.total_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {plan.currency}
                </span>
              </div>
              <div className="text-xs text-slate-500 font-mono">
                Order ID: <span className="text-slate-800 font-semibold">{paypalOrderId}</span>
              </div>
            </div>

            {/* PayPal Checkout Execution Box */}
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 text-center space-y-4 mb-4">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-slate-200 text-[#0070E0] text-xs font-semibold">
                <ShieldCheck className="w-4 h-4 text-[#0070E0]" />
                <span>Verified PayPal Sandbox Integration</span>
              </div>
              <p className="text-xs text-slate-600 max-w-sm mx-auto">
                Authorize payment in PayPal Sandbox and capture the transaction.
              </p>

              {approvalUrl && !approvalUrl.includes("MOCK-") && (
                <a
                  href={approvalUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-[#0070E0] hover:underline font-mono py-1"
                >
                  <span>Launch Sandbox Approval Window</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}

              {/* PayPal Primary Action Button */}
              <button
                onClick={handleCapturePayment}
                className="w-full py-3.5 rounded-full bg-[#FFC439] hover:bg-[#F4BB34] text-[#003087] font-extrabold text-sm tracking-wide shadow-sm hover:shadow transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <span>Pay with</span>
                <span className="italic font-black text-base">PayPal</span>
                <span className="text-xs font-normal text-slate-700 ml-1">(Sandbox)</span>
              </button>
            </div>

            <button
              onClick={() => setStep("AWAITING_APPROVAL")}
              className="w-full text-center text-xs text-slate-500 hover:text-slate-800 py-1 cursor-pointer"
            >
              Cancel and return to Purchase Plan
            </button>
          </div>
        )}

        {/* State: Capturing Payment */}
        {step === "CAPTURING" && (
          <div className="py-16 text-center space-y-3">
            <Loader2 className="w-8 h-8 text-[#0070E0] animate-spin mx-auto" />
            <h3 className="text-base font-bold text-[#14213D]">
              Verifying Payment with PayPal...
            </h3>
            <p className="text-xs text-slate-500">
              Executing authoritative server-side order capture.
            </p>
          </div>
        )}

        {/* State: Payment Successful */}
        {step === "SUCCESS" && plan && payment && (
          <div className="py-4 text-center">
            {/* Green Check Icon */}
            <div className="w-16 h-16 rounded-full bg-emerald-50 border-2 border-emerald-400 flex items-center justify-center mx-auto mb-4 text-emerald-600 shadow-sm">
              <CheckCircle2 className="w-9 h-9" />
            </div>

            <h3 className="text-2xl font-black text-[#14213D] tracking-tight mb-1">
              Payment Successful
            </h3>
            <p className="text-xs text-emerald-700 font-semibold mb-6">
              Verified by PayPal Sandbox &bull; Status: {payment.status}
            </p>

            {/* Receipt Card */}
            <div className="rounded-2xl bg-[#F5F8FC] border border-slate-200 p-4 text-left space-y-2.5 text-xs text-slate-700 mb-6 font-mono">
              <div className="flex justify-between border-b border-slate-200/80 pb-2">
                <span className="text-slate-500 font-sans">Item</span>
                <span className="font-bold text-slate-900 font-sans">{plan.product_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Amount Paid</span>
                <span className="text-[#003087] font-black text-sm">
                  ${payment.amount.toLocaleString("en-US", { minimumFractionDigits: 2 })} {payment.currency}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">Provider</span>
                <span className="text-slate-900 font-semibold font-sans">PayPal Sandbox</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 font-sans">PayPal Order ID</span>
                <span className="text-slate-800 font-medium truncate max-w-[200px]">{payment.provider_order_id}</span>
              </div>
              {payment.capture_id && (
                <div className="flex justify-between">
                  <span className="text-slate-500 font-sans">Capture ID</span>
                  <span className="text-slate-800 font-medium">{payment.capture_id}</span>
                </div>
              )}
              {payment.payer_email && (
                <div className="flex justify-between border-t border-slate-200/80 pt-2">
                  <span className="text-slate-500 font-sans">Buyer Account</span>
                  <span className="text-slate-800 truncate max-w-[200px]">{payment.payer_email}</span>
                </div>
              )}
            </div>

            {/* Finish Action */}
            <button
              onClick={onClose}
              className="w-full py-3.5 rounded-2xl bg-[#0070E0] hover:bg-[#005bb5] text-white font-bold text-sm transition-all shadow-sm cursor-pointer"
            >
              Back to Shopping
            </button>
          </div>
        )}

        {/* State: Failure */}
        {step === "FAILED" && (
          <div className="py-6 text-center space-y-4">
            <div className="w-14 h-14 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center mx-auto text-rose-600">
              <AlertCircle className="w-7 h-7" />
            </div>
            <h3 className="text-lg font-bold text-[#14213D]">Payment Incomplete</h3>
            <p className="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
              {errorMessage || "Payment wasn't completed. Your Purchase Plan has not been marked as paid."}
            </p>
            <div className="flex gap-3 justify-center pt-2">
              <button
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl border border-slate-200 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={() => setStep("AWAITING_APPROVAL")}
                className="px-5 py-2.5 rounded-xl bg-[#0070E0] hover:bg-[#005bb5] text-white text-xs font-bold cursor-pointer"
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
