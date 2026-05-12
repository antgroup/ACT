import type { ISR } from '../types/common';

export interface CartItem {
  product_id: string;
  product_name: string;
  price: number;
  currency: string;
  quantity: number;
}

export interface CartConfirmationResult {
  confirmed: boolean;
  order_no?: string;
  cart_snapshot_digest?: string;
  violations?: string[];
}

export class CartConfirmation {
  performRuleCheck(isr: ISR, cartItems: CartItem[]): { passed: boolean; violations: string[] } {
    const violations: string[] = [];
    const totalAmount = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);

    if (isr.max_total_amount && totalAmount > isr.max_total_amount) {
      violations.push(`Total amount ${totalAmount} exceeds max_total_amount ${isr.max_total_amount}`);
    }

    if (isr.ext?.commerce?.max_single_amount) {
      for (const item of cartItems) {
        if (item.price > isr.ext.commerce.max_single_amount) {
          violations.push(`Item ${item.product_id} price ${item.price} exceeds max_single_amount`);
        }
      }
    }

    return { passed: violations.length === 0, violations };
  }
}