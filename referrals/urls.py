from django.urls import path
from .views import (
    ReferralListView,
    GenerateReferralCodeView,
    ReferralStatsView,
    ReferralRewardsView,
    ClaimRewardView,
)

urlpatterns = [
    path('', ReferralListView.as_view()),                    # GET  /api/referrals/
    path('generate-code/', GenerateReferralCodeView.as_view()), # POST /api/referrals/generate-code/
    path('stats/', ReferralStatsView.as_view()),             # GET  /api/referrals/stats/
    path('rewards/', ReferralRewardsView.as_view()),         # GET  /api/referrals/rewards/
    path('claim/', ClaimRewardView.as_view()),               # POST /api/referrals/claim/
]