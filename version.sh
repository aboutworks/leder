#!/bin/bash
set -e  # 遇到错误立即退出

# ===================== 可配置参数（修改这里即可）=====================
# 提交描述（支持换行，保留原有信息）
COMMIT_MSG="V1.0.2"
# 版本号（核心配置，改这里就能更新版本）
VERSION="V1.0.2"
# 版本描述（与版本号对应）
VERSION_MSG="版本${VERSION}"
# ==================================================================

# 颜色输出（增强提示）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # 重置颜色

# 步骤1：检查Git工作区状态
echo -e "${YELLOW}🔍 检查Git工作区状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ 发现未提交文件，执行git add...${NC}"
    git add --all
else
    echo -e "${YELLOW}ℹ️  工作区无未提交文件，跳过git add${NC}"
fi

# 步骤2：提交代码
echo -e "${YELLOW}📝 执行git commit...${NC}"
git commit -m "${COMMIT_MSG}" || {
    echo -e "${RED}❌ commit失败（可能无文件变更）${NC}"
    # 无文件变更时仍继续执行后续步骤（避免脚本中断）
}

# 步骤3：打标签
echo -e "${YELLOW}🏷️  创建标签${VERSION}...${NC}"
# 先删除本地同名标签（避免重复）
git tag -d "${VERSION}" 2>/dev/null || true
git tag -a "${VERSION}" -m "${VERSION_MSG}"

# 步骤4：推送代码和标签
echo -e "${YELLOW}🚀 推送代码和标签到远程...${NC}"
git push --all
git push origin "${VERSION}"

# 完成提示
echo -e "\n${GREEN}🎉 操作完成！"
echo -e "📌 提交信息：${COMMIT_MSG}"
echo -e "🏷️  推送版本：${VERSION}（描述：${VERSION_MSG}）${NC}"