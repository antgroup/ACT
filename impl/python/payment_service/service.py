"""
支付服务模块
提供订单支付处理能力
这是一个独立的服务模块，不是 Agent
"""
import random
import string
from typing import Dict, Optional
from datetime import datetime


class PaymentService:
    """
    支付服务类
    职责：处理订单支付、验证金额、生成支付流水
    """
    
    def __init__(self, merchant_service):
        """
        初始化支付服务
        
        Args:
            merchant_service: 商户服务实例（用于查询和更新订单）
        """
        self.merchant_service = merchant_service
        # 支付记录数据库
        self.payments: Dict[str, Dict] = {}
        
        print("[支付服务] 初始化完成")
    
    def process_payment(self, order_id: str, amount: float, payment_method: str = "mock_payment") -> Dict:
        """
        处理支付请求
        
        Args:
            order_id: 订单ID
            amount: 支付金额
            payment_method: 支付方式
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 支付信息,
                "message": str
            }
        """
        try:
            # 1. 查询订单
            order_result = self.merchant_service.get_order(order_id)
            
            if not order_result["success"]:
                return {
                    "success": False,
                    "data": None,
                    "message": f"订单不存在: {order_id}"
                }
            
            order = order_result["data"]
            
            # 2. 检查订单状态
            if order["status"] == "paid":
                return {
                    "success": False,
                    "data": None,
                    "message": "订单已支付，请勿重复支付"
                }
            
            if order["status"] == "cancelled":
                return {
                    "success": False,
                    "data": None,
                    "message": "订单已取消，无法支付"
                }
            
            # 3. 验证金额
            expected_amount = order["total_amount"]
            if abs(amount - expected_amount) > 0.01:
                return {
                    "success": False,
                    "data": None,
                    "message": f"支付金额不正确，应付: ¥{expected_amount:.2f}, 实付: ¥{amount:.2f}"
                }
            
            # 4. 生成支付流水号
            payment_id = "PAY" + ''.join(random.choices(string.digits, k=10))
            
            # 5. 模拟支付处理（实际场景会调用第三方支付接口）
            payment_status = self._mock_payment_process(payment_id, amount)
            
            if not payment_status["success"]:
                return {
                    "success": False,
                    "data": None,
                    "message": f"支付处理失败: {payment_status['message']}"
                }
            
            # 6. 创建支付记录
            payment = {
                "payment_id": payment_id,
                "order_id": order_id,
                "amount": amount,
                "payment_method": payment_method,
                "status": "success",
                "created_at": datetime.now().isoformat(),
                "transaction_id": payment_status.get("transaction_id")
            }
            
            # 7. 保存支付记录
            self.payments[payment_id] = payment
            
            # 8. 更新订单状态
            update_result = self.merchant_service.update_order_status(
                order_id=order_id,
                status="paid",
                payment_id=payment_id
            )
            
            if not update_result["success"]:
                # 支付成功但订单更新失败（实际场景需要回滚或补偿）
                print(f"[支付服务] 警告: 支付成功但订单更新失败 - {order_id}")
            
            print(f"[支付服务] 支付成功: {payment_id}, 订单: {order_id}, 金额: ¥{amount:.2f}")
            
            return {
                "success": True,
                "data": payment.copy(),
                "message": f"支付成功，支付流水号: {payment_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"支付处理异常: {str(e)}"
            }
    
    def _mock_payment_process(self, payment_id: str, amount: float) -> Dict:
        """
        模拟支付处理（实际场景会调用第三方支付接口）
        
        Args:
            payment_id: 支付ID
            amount: 金额
            
        Returns:
            Dict: 支付处理结果
        """
        # 模拟支付成功（实际场景可能失败）
        # 这里可以模拟各种支付场景：成功、失败、超时等
        
        # 生成模拟交易号
        transaction_id = "TXN" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": "支付处理成功"
        }
    
    def get_payment(self, payment_id: str) -> Dict:
        """
        查询支付记录
        
        Args:
            payment_id: 支付流水号
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 支付信息,
                "message": str
            }
        """
        try:
            if payment_id not in self.payments:
                return {
                    "success": False,
                    "data": None,
                    "message": f"支付记录 {payment_id} 不存在"
                }
            
            return {
                "success": True,
                "data": self.payments[payment_id].copy(),
                "message": "获取支付记录成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"查询支付记录失败: {str(e)}"
            }
    
    def get_payment_by_order(self, order_id: str) -> Dict:
        """
        根据订单ID查询支付记录
        
        Args:
            order_id: 订单ID
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 支付信息,
                "message": str
            }
        """
        try:
            for payment in self.payments.values():
                if payment["order_id"] == order_id:
                    return {
                        "success": True,
                        "data": payment.copy(),
                        "message": "获取支付记录成功"
                    }
            
            return {
                "success": False,
                "data": None,
                "message": f"订单 {order_id} 没有支付记录"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"查询支付记录失败: {str(e)}"
            }
    
    def refund_payment(self, payment_id: str, reason: str = "用户申请退款") -> Dict:
        """
        退款处理（扩展功能）
        
        Args:
            payment_id: 支付流水号
            reason: 退款原因
            
        Returns:
            Dict: {
                "success": bool,
                "data": Dict 退款信息,
                "message": str
            }
        """
        try:
            # 查询支付记录
            payment_result = self.get_payment(payment_id)
            
            if not payment_result["success"]:
                return {
                    "success": False,
                    "data": None,
                    "message": "支付记录不存在"
                }
            
            payment = payment_result["data"]
            
            if payment["status"] == "refunded":
                return {
                    "success": False,
                    "data": None,
                    "message": "该支付已退款"
                }
            
            # 生成退款流水号
            refund_id = "REF" + ''.join(random.choices(string.digits, k=10))
            
            # 更新支付状态
            self.payments[payment_id]["status"] = "refunded"
            self.payments[payment_id]["refund_id"] = refund_id
            self.payments[payment_id]["refund_reason"] = reason
            self.payments[payment_id]["refunded_at"] = datetime.now().isoformat()
            
            # 更新订单状态
            self.merchant_service.update_order_status(
                order_id=payment["order_id"],
                status="refunded"
            )
            
            print(f"[支付服务] 退款成功: {refund_id}, 支付: {payment_id}")
            
            return {
                "success": True,
                "data": {
                    "refund_id": refund_id,
                    "payment_id": payment_id,
                    "amount": payment["amount"],
                    "reason": reason
                },
                "message": f"退款成功，退款流水号: {refund_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"退款处理失败: {str(e)}"
            }
    
    def get_all_payments(self) -> Dict:
        """
        获取所有支付记录
        
        Returns:
            Dict: {
                "success": bool,
                "data": List[Dict] 支付记录列表,
                "message": str
            }
        """
        try:
            return {
                "success": True,
                "data": list(self.payments.values()),
                "total_count": len(self.payments),
                "message": "获取支付记录列表成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "message": f"获取支付记录列表失败: {str(e)}"
            }