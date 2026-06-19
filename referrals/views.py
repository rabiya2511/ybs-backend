from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Referral, ReferralReward


# ══════════════════════════════════════════════
# GET /api/referrals/
# List all referrals made by logged in user
# ══════════════════════════════════════════════
class ReferralListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        referrals = Referral.objects.filter(referred_by=request.user)

        data = [{
            'id': str(r.id),
            'referred_email': r.referred_email,
            'referred_name': r.referred_user.name if r.referred_user else None,
            'status': r.status,
            'reward_amount': str(r.reward_amount),
            'reward_claimed': r.reward_claimed,
            'converted_at': r.converted_at,
            'created_at': r.created_at,
        } for r in referrals]

        return Response({
            'success': True,
            'count': len(data),
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/referrals/generate-code/
# Get or regenerate referral code
# ══════════════════════════════════════════════
class GenerateReferralCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Code already exists on user model — just return it
        if not user.referral_code:
            import random, string
            user.referral_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            user.save()

        referral_link = f"https://ybs.in/register?ref={user.referral_code}"

        return Response({
            'success': True,
            'data': {
                'referral_code': user.referral_code,
                'referral_link': referral_link,
                'reward_per_referral': '₹500',
            }
        })


# ══════════════════════════════════════════════
# GET /api/referrals/stats/
# Referral statistics for logged in user
# ══════════════════════════════════════════════
class ReferralStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        referrals = Referral.objects.filter(referred_by=request.user)

        total_referrals  = referrals.count()
        converted        = referrals.filter(status='Converted').count()
        pending          = referrals.filter(status='Pending').count()
        total_earned     = converted * 500
        claimed          = referrals.filter(reward_claimed=True).count()
        unclaimed        = converted - claimed

        conversion_rate = round((converted / total_referrals * 100), 1) if total_referrals > 0 else 0

        return Response({
            'success': True,
            'data': {
                'referral_code': request.user.referral_code,
                'total_referrals': total_referrals,
                'converted': converted,
                'pending': pending,
                'conversion_rate': f"{conversion_rate}%",
                'total_earned': f"₹{total_earned}",
                'claimed_rewards': claimed,
                'unclaimed_rewards': unclaimed,
                'wallet_balance': str(request.user.wallet_balance),
            }
        })


# ══════════════════════════════════════════════
# GET /api/referrals/rewards/
# List all rewards for logged in user
# ══════════════════════════════════════════════
class ReferralRewardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rewards = ReferralReward.objects.filter(user=request.user)

        data = [{
            'id': str(r.id),
            'referral_email': r.referral.referred_email,
            'amount': str(r.amount),
            'is_claimed': r.is_claimed,
            'claimed_at': r.claimed_at,
            'created_at': r.created_at,
        } for r in rewards]

        total_unclaimed = rewards.filter(
            is_claimed=False
        ).count() * 500

        return Response({
            'success': True,
            'count': len(data),
            'total_unclaimed': f"₹{total_unclaimed}",
            'data': data
        })


# ══════════════════════════════════════════════
# POST /api/referrals/claim/
# Claim a referral reward → adds to wallet
# ══════════════════════════════════════════════
class ClaimRewardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reward_id = request.data.get('reward_id')

        if not reward_id:
            return Response({
                'success': False,
                'message': 'reward_id is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            reward = ReferralReward.objects.get(
                id=reward_id,
                user=request.user,
                is_claimed=False
            )
        except ReferralReward.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Reward not found or already claimed.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Mark reward as claimed
        reward.is_claimed  = True
        reward.claimed_at  = timezone.now()
        reward.save()

        # Add to wallet
        request.user.wallet_balance += reward.amount
        request.user.save()

        # Mark referral as claimed
        reward.referral.reward_claimed = True
        reward.referral.save()

        return Response({
            'success': True,
            'message': f'₹{reward.amount} credited to your wallet!',
            'data': {
                'amount_credited': str(reward.amount),
                'new_wallet_balance': str(request.user.wallet_balance),
            }
        })