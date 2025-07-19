# DataHerd 项目优化任务清单

## 阶段 1: 下载项目并分析现状
- [x] 下载项目到本地
- [x] 查看项目结构
- [x] 分析 README.md 和主要文档
- [x] 检查主要 Python 文件
- [x] 识别 MateGen 残余信息
- [x] 分析数据库结构
- [x] 检查启动方式

### 发现的问题：
1. MateGen 残余信息：
   - README.md: "Built on the foundation of MateGenPro framework"
   - config/config.py: 日志文件名 'mategen_runtime.log'
   - api_server/func_router.py: 导入和使用 MateGenClass
   - api_server/init_interface.py: MateGenClass 相关代码
   - server/agent/create_assistant.py: assistant_name = "MateGen-Pro"
   - server/utils.py: "mategen Class" 注释
   - tools/tool_desc.py: "你是MateGen" 描述

2. 数据库结构良好，专门为牛群数据清洗设计
3. 启动方式：通过 python api_server/api_router.py 启动

## 阶段 2: 替换 MateGen 残余信息为 DataHerd
- [x] 搜索所有文件中的 MateGen 相关内容
- [x] 替换为 DataHerd 相关信息
- [x] 更新项目描述和文档
- [x] 删除不再使用的 MateGen 相关文件

### 已完成的替换：
- README.md: 替换框架描述
- config/config.py: 更改日志文件名
- server/agent/create_assistant.py: 更新 assistant 名称和指令
- server/utils.py: 更新注释
- tools/tool_desc.py: 完全重写指令内容
- 删除文件: func_router.py, init_interface.py, pytanic_router.py

## 阶段 3: 审查和优化数据库处理
- [x] 检查数据库模型和架构
- [x] 审查数据处理逻辑
- [x] 优化数据库操作

### 发现的问题：
1. base_model.py 包含大量 MateGen 残余模型（SecretModel, ThreadModel, KnowledgeBase 等）
2. schemas.py 中的模型设计良好，专门为牛群数据清洗设计
3. dataherd 模块中的处理器设计合理，但目前是占位符实现
4. 数据库初始化导入了不必要的 MateGen 模型

## 阶段 4: 精简项目结构和代码
- [x] 移除冗余文件和代码
- [x] 优化代码结构
- [x] 统一代码风格

### 已完成的精简：
1. 创建新的简化数据库模型文件 db/models.py
2. 更新数据库初始化文件，移除 MateGen 模型依赖
3. 删除不再需要的文件：
   - db/base_model.py, db/insert_test_data.py
   - server/agent/, server/identity_verification/, server/cache/
   - tools/ 整个目录
4. 简化 server/utils.py，只保留必要功能
5. 更新 api_router.py 的导入语句

## 阶段 5: 完善 requirements 和环境配置
- [x] 检查 requirements.txt
- [x] 验证依赖完整性
- [x] 优化环境配置

### 已完成的优化：
1. 精简 requirements.txt，移除不必要的依赖
2. 添加了 pandas 依赖用于数据处理
3. 按功能分组组织依赖
4. .env.example 文件配置完善

## 阶段 6: 统一启动方式并创建简易启动脚本
- [x] 分析当前启动方式
- [x] 创建统一启动脚本
- [x] 编写启动文档

### 已完成的启动优化：
1. 创建 start.py 统一启动脚本，支持多种选项
2. 创建 start.sh 快速启动脚本，自动处理环境设置
3. 更新 README.md，提供 4 种启动方式
4. 添加环境检查、数据库初始化、前端构建等功能

## 阶段 7: 测试项目运行并推送到 GitHub
- [ ] 测试项目启动
- [ ] 验证功能正常
- [ ] 推送所有更改到 GitHub

