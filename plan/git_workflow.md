# Git 工作流程和提交规范

## 分支策略

本项目采用基于功能分支的Git工作流程，主要分支结构如下：

- **main**: 主分支，包含稳定的生产就绪代码
- **develop**: 开发分支，包含最新的开发代码
- **feature/xxx**: 功能分支，用于开发新功能
- **bugfix/xxx**: 修复分支，用于修复bug
- **release/x.x.x**: 发布分支，用于准备新版本发布

## 工作流程

1. **功能开发**：
   - 从`develop`分支创建新的功能分支：`git checkout -b feature/功能名称 develop`
   - 在功能分支上进行开发和提交
   - 完成功能后，将`develop`分支合并到功能分支以解决冲突：`git merge develop`
   - 提交Pull Request将功能分支合并到`develop`分支

2. **Bug修复**：
   - 从`develop`分支（或对于生产环境的紧急修复，从`main`分支）创建修复分支：`git checkout -b bugfix/问题描述 develop`
   - 在修复分支上进行修复和提交
   - 完成修复后，提交Pull Request将修复分支合并到相应分支

3. **版本发布**：
   - 从`develop`分支创建发布分支：`git checkout -b release/x.x.x develop`
   - 在发布分支上进行最终测试和修复
   - 发布准备就绪后，将发布分支合并到`main`和`develop`分支
   - 在`main`分支上创建版本标签：`git tag -a vx.x.x -m "版本x.x.x"`

## 提交规范

为了保持提交历史的清晰和一致，所有提交消息应遵循以下格式：

```
<类型>(<范围>): <简短描述>

<详细描述>

<关闭的问题>
```

### 类型

- **feat**: 新功能
- **fix**: 修复bug
- **docs**: 文档更改
- **style**: 不影响代码含义的更改（空格、格式化、缺少分号等）
- **refactor**: 既不修复bug也不添加功能的代码更改
- **perf**: 提高性能的代码更改
- **test**: 添加或修正测试
- **chore**: 对构建过程或辅助工具和库的更改

### 范围

范围是可选的，用于指定更改的模块或组件：

- **data**: 数据处理模块
- **viz**: 可视化模块
- **analysis**: 分析模块
- **ui**: 用户界面
- **config**: 配置系统
- **core**: 核心功能
- **docs**: 文档
- **tests**: 测试

### 示例

```
feat(viz): 添加散点图支持

实现了散点图类型，支持基本的点样式和颜色映射功能。
添加了相关的单元测试和文档。

Closes #123
```

```
fix(data): 修复CSV导入中的编码问题

修复了在导入非UTF-8编码的CSV文件时出现的字符错误。
现在会自动检测文件编码并正确处理。

Closes #456
```

## 自动提交脚本

为了简化Git提交过程，可以使用以下脚本自动生成符合规范的提交消息：

```bash
#!/bin/bash

# 获取类型
echo "选择提交类型:"
echo "1) feat:    新功能"
echo "2) fix:     修复bug"
echo "3) docs:    文档更改"
echo "4) style:   代码风格更改"
echo "5) refactor: 代码重构"
echo "6) perf:    性能改进"
echo "7) test:    测试相关"
echo "8) chore:   构建/工具相关"
read -p "输入选项 (1-8): " type_option

case $type_option in
    1) type="feat";;    
    2) type="fix";;     
    3) type="docs";;    
    4) type="style";;   
    5) type="refactor";;
    6) type="perf";;    
    7) type="test";;    
    8) type="chore";;   
    *) echo "无效选项"; exit 1;;
esac

# 获取范围
echo "\n选择范围 (可选):"
echo "1) data:    数据处理模块"
echo "2) viz:     可视化模块"
echo "3) analysis: 分析模块"
echo "4) ui:      用户界面"
echo "5) config:  配置系统"
echo "6) core:    核心功能"
echo "7) docs:    文档"
echo "8) tests:   测试"
echo "9) 自定义范围"
echo "0) 无范围"
read -p "输入选项 (0-9): " scope_option

case $scope_option in
    1) scope="data";;    
    2) scope="viz";;     
    3) scope="analysis";;
    4) scope="ui";;      
    5) scope="config";;  
    6) scope="core";;    
    7) scope="docs";;    
    8) scope="tests";;   
    9) read -p "输入自定义范围: " scope;;
    0) scope="";;        
    *) echo "无效选项"; exit 1;;
esac

# 获取简短描述
read -p "\n输入简短描述: " description

# 获取详细描述
echo "\n输入详细描述 (可选，按Ctrl+D结束):"
detailed_description=$(cat)

# 获取关闭的问题
read -p "\n关闭的问题编号 (可选，例如 #123): " issue

# 构建提交消息
if [ -z "$scope" ]; then
    commit_message="$type: $description"
else
    commit_message="$type($scope): $description"
fi

if [ ! -z "$detailed_description" ]; then
    commit_message="$commit_message\n\n$detailed_description"
fi

if [ ! -z "$issue" ]; then
    if [[ $issue == \#* ]]; then
        commit_message="$commit_message\n\nCloses $issue"
    else
        commit_message="$commit_message\n\nCloses #$issue"
    fi
fi

# 显示提交消息预览
echo "\n提交消息预览:"
echo "-------------------"
echo -e "$commit_message"
echo "-------------------"

# 确认提交
read -p "\n确认提交? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    echo -e "$commit_message" | git commit -F -
    echo "提交成功!"
else
    echo "提交已取消"
fi
```

## 代码审查指南

在审查Pull Request时，请关注以下几点：

1. **功能完整性**：确保实现了所有需求
2. **代码质量**：代码是否清晰、简洁、易于理解
3. **测试覆盖**：是否有足够的测试覆盖新功能或修复
4. **文档**：是否更新了相关文档
5. **性能**：代码是否有性能问题
6. **兼容性**：更改是否破坏了现有功能

## 版本号规范

本项目使用语义化版本号（[SemVer](https://semver.org/lang/zh-CN/)）：

- **主版本号**：当进行不兼容的API更改时增加
- **次版本号**：当添加向后兼容的功能时增加
- **修订号**：当进行向后兼容的bug修复时增加

例如：1.2.3表示主版本1，次版本2，修订版3。