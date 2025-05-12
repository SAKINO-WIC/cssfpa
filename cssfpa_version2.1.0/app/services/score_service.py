from app import db
from app.models.student import Student
from app.models.score_config import ScoreConfig, StudentScore
from app.models.user import User
import re
import logging

logger = logging.getLogger(__name__)

class ScoreService:
    """学生综合评分计算服务"""
    
    @staticmethod
    def identify_scholarship(text):
        """识别奖学金类型和等级"""
        if not text or not isinstance(text, str):
            return {'national': None, 'school': None}
            
        # 初始化结果
        result = {
            'national': None,
            'school': None
        }
        
        # 国家级关键词
        national_keywords = ["国家级", "国家奖学金", "国奖"]
        # 校级关键词
        school_keywords = ["校级", "校奖学金", "校奖", "优秀学生奖学金"]
        
        # 检测国家级
        for kw in national_keywords:
            if kw in text:
                # 识别等级
                if "一等" in text or "一级" in text or "特等" in text:
                    result['national'] = 'first'
                elif "二等" in text or "二级" in text:
                    result['national'] = 'second'
                elif "三等" in text or "三级" in text:
                    result['national'] = 'third'
                break
        
        # 检测校级
        for kw in school_keywords:
            if kw in text:
                # 识别等级
                if "一等" in text or "一级" in text or "特等" in text:
                    result['school'] = 'first'
                elif "二等" in text or "二级" in text:
                    result['school'] = 'second'
                elif "三等" in text or "三级" in text:
                    result['school'] = 'third'
                break
        
        return result
    
    @staticmethod
    def calculate_scholarship_score(student, config):
        """计算奖学金得分"""
        # 确保使用配置字典而不是ScoreConfig对象
        config_data = config.config if hasattr(config, 'config') else config
        scholarship_settings = config_data.get('scholarship_settings', {})
        
        # 初始化分数
        national_score = 0
        school_score = 0
        
        # 识别奖学金
        if student.scholarship:
            scholarship_result = ScoreService.identify_scholarship(student.scholarship)
            
            # 计算国家级奖学金得分
            if scholarship_result['national'] == 'first':
                national_score = scholarship_settings.get('national_first', 10)
            elif scholarship_result['national'] == 'second':
                national_score = scholarship_settings.get('national_second', 8)
            elif scholarship_result['national'] == 'third':
                national_score = scholarship_settings.get('national_third', 6)
            
            # 计算校级奖学金得分
            if scholarship_result['school'] == 'first':
                school_score = scholarship_settings.get('school_first', 5)
            elif scholarship_result['school'] == 'second':
                school_score = scholarship_settings.get('school_second', 3)
            elif scholarship_result['school'] == 'third':
                school_score = scholarship_settings.get('school_third', 2)
        else:
            scholarship_result = {'national': None, 'school': None}
        
        # 总分是两项得分之和
        total_score = national_score + school_score
        
        return {
            'national_level': scholarship_result['national'],
            'school_level': scholarship_result['school'],
            'national_score': national_score,
            'school_score': school_score,
            'total_score': total_score
        }
    
    @staticmethod
    def calculate_volunteer_score(student, config):
        """计算志愿服务得分"""
        # 使用新的分级评分标准，与界面显示一致
        hours = student.volunteer_hours or 0
        
        # 初始化得分
        score = 0
        
        # 按照新的分级标准计算得分
        if hours > 50:  # 51小时以上
            score = 5
        elif hours > 30:  # 31-50小时
            score = 4
        elif hours > 15:  # 16-30小时
            score = 3
        elif hours > 5:   # 6-15小时
            score = 2
        elif hours > 0:   # 1-5小时
            score = 1
        else:             # 0小时
            score = 0
            
        # 记录详细信息以便调试
        logger.info(f"志愿服务时长 {hours} 小时，得分: {score}分")
        
        return {
            'hours': hours,
            'score': score
        }
    
    @staticmethod
    def calculate_english_score(student, config):
        """计算英语能力得分"""
        # 确保使用配置字典而不是ScoreConfig对象
        config_data = config.config if hasattr(config, 'config') else config
        english_settings = config_data.get('english_settings', {})
        
        # 获取各项配置参数
        cet4_pass_score = english_settings.get('cet4_pass_score', 425)
        cet6_pass_score = english_settings.get('cet6_pass_score', 425)
        
        # CET4 分数段配置
        cet4_level1_points = english_settings.get('cet4_level1_points', 1)  # 425-450
        cet4_level2_points = english_settings.get('cet4_level2_points', 2)  # 451-500
        cet4_level3_points = english_settings.get('cet4_level3_points', 3)  # 501-550
        cet4_level4_points = english_settings.get('cet4_level4_points', 4)  # 551-600
        cet4_level5_points = english_settings.get('cet4_level5_points', 5)  # 600+
        
        # CET6 分数段配置
        cet6_level1_points = english_settings.get('cet6_level1_points', 3)  # 425-450
        cet6_level2_points = english_settings.get('cet6_level2_points', 5)  # 451-500
        cet6_level3_points = english_settings.get('cet6_level3_points', 6)  # 501-550
        cet6_level4_points = english_settings.get('cet6_level4_points', 8)  # 551-600
        cet6_level5_points = english_settings.get('cet6_level5_points', 10) # 600+
        
        # 初始化英语得分
        cet4_point = 0
        cet6_point = 0
        cet4_passed = False
        
        # 计算四级得分
        if student.cet4_score and student.cet4_score >= cet4_pass_score:
            cet4_passed = True
            
            # 根据分数段设置得分
            if student.cet4_score >= 600:
                cet4_point = cet4_level5_points
            elif student.cet4_score >= 551:
                cet4_point = cet4_level4_points
            elif student.cet4_score >= 501:
                cet4_point = cet4_level3_points
            elif student.cet4_score >= 451:
                cet4_point = cet4_level2_points
            elif student.cet4_score >= 425:
                cet4_point = cet4_level1_points
        
        # 计算六级得分（需要先通过四级）
        if cet4_passed and student.cet6_score and student.cet6_score >= cet6_pass_score:
            # 根据分数段设置得分
            if student.cet6_score >= 600:
                cet6_point = cet6_level5_points
            elif student.cet6_score >= 551:
                cet6_point = cet6_level4_points
            elif student.cet6_score >= 501:
                cet6_point = cet6_level3_points
            elif student.cet6_score >= 451:
                cet6_point = cet6_level2_points
            elif student.cet6_score >= 425:
                cet6_point = cet6_level1_points
        
        # 四级和六级分数可叠加，但总分不超过10分
        total_score = min(cet4_point + cet6_point, 10)
        
        return {
            'cet4_score': student.cet4_score,
            'cet6_score': student.cet6_score,
            'cet4_passed': cet4_passed,
            'cet4_point': cet4_point,
            'cet6_point': cet6_point,
            'total_score': total_score
        }
    
    @staticmethod
    def calculate_academic_score(student, config):
        """计算学业表现得分"""
        # 确保使用配置字典而不是ScoreConfig对象
        config_data = config.config if hasattr(config, 'config') else config
        academic_weight = config_data.get('academic_weight', 0.15)
        
        # 获取综测成绩，如果不存在则为0
        comprehensive_test_score = student.comprehensive_test_score or 0
        
        # 计算得分
        score = comprehensive_test_score * academic_weight
        
        # 返回包含详细信息的字典
        return score
    
    @staticmethod
    def check_base_conditions(student):
        """检查学生是否满足入党积极分子的基本条件"""
        # 基本条件检查
        has_application = getattr(student, 'has_application', False)
        passed_exam = getattr(student, 'passed_exam', False)
        class_approved = getattr(student, 'class_approved', False)
        
        # 检查挂科记录 - 使用现有的has_failed_course字段，需要反转其含义
        # no_failed_course 表示"无挂科记录"，而has_failed_course表示"有挂科记录"
        has_failed_course = getattr(student, 'has_failed_course', False)
        no_failed_course = not has_failed_course  # 反转含义
        
        # 调试信息
        logger.debug(f"学生 {student.student_id} 基础条件检查:")
        logger.debug(f"  - 入党申请书: {has_application}")
        logger.debug(f"  - 通过党课考试: {passed_exam}")
        logger.debug(f"  - 班级推优: {class_approved}")
        logger.debug(f"  - 有挂科记录: {has_failed_course}")
        logger.debug(f"  - 无挂科记录(反转): {no_failed_course}")
        
        # 所有条件必须满足
        passed_all = has_application and passed_exam and class_approved and no_failed_course
        
        # 组织返回结果
        return {
            'passed_all': passed_all,
            'base_conditions': {
                'has_application': has_application,
                'passed_exam': passed_exam,
                'class_approved': class_approved,
                'no_failed_course': no_failed_course
            }
        }
    
    @staticmethod
    def calculate_total_score(student, config=None):
        """计算学生的综合评分"""
        try:
            if not config:
                config = ScoreConfig.get_default_config()
                logger.warning(f"没有提供评分配置，使用默认配置: {config.id}")
            else:
                logger.info(f"使用评分配置: {config.name} (ID: {config.id})")
            
            # 获取配置
            config_data = config.config
            
            # 记录学生信息
            student_info = {
                'student_id': getattr(student, 'student_id', 'Unknown'),
                'name': getattr(student, 'name', 'Unknown')
            }
            logger.info(f"计算学生 {student_info['student_id']} ({student_info['name']}) 的评分")
            
            # 检查学生数据完整性并进行类型转换
            missing_fields = []
            
            # 转换布尔字段 (处理字符串 "0"/"1" 和 0/1/None 的情况)
            boolean_fields = ["has_application", "passed_exam", "class_approved", "has_failed_course"]
            for field in boolean_fields:
                value = getattr(student, field, None)
                if value is None:
                    missing_fields.append(f"{field} (布尔字段)")
                else:
                    # 尝试转换字符串或数值为布尔值
                    if isinstance(value, str):
                        if value.lower() in ('1', 'true', 'yes', 'y'):
                            setattr(student, field, True)
                        elif value.lower() in ('0', 'false', 'no', 'n'):
                            setattr(student, field, False)
                        else:
                            # 无法解析的字符串
                            missing_fields.append(f"{field} (无效的布尔值: {value})")
                    elif isinstance(value, (int, float)):
                        setattr(student, field, bool(value))
            
            # 转换数值字段 (处理字符串形式的数值)
            numeric_fields = [("comprehensive_test_score", "综合测评成绩"), ("volunteer_hours", "志愿服务时长")]
            for field, desc in numeric_fields:
                value = getattr(student, field, None)
                if value is None:
                    missing_fields.append(f"{field} ({desc})")
                else:
                    # 尝试转换字符串为数值
                    if isinstance(value, str):
                        try:
                            numeric_value = float(value)
                            setattr(student, field, numeric_value)
                        except ValueError:
                            # 无法转换为数值的字符串
                            missing_fields.append(f"{field} (无效的数值: {value})")
            
            # 如果缺少必要字段，抛出异常
            if missing_fields:
                error_msg = f"学生数据不完整或无效，问题字段: {', '.join(missing_fields)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 检查基础条件
            base_conditions = ScoreService.check_base_conditions(student)
            passed_base_conditions = base_conditions['passed_all']
            logger.info(f"基础条件检查结果: {passed_base_conditions}")
            
            # 如果基础条件不满足，得分为0
            if not passed_base_conditions:
                base_score = 0
                logger.info("基础条件不满足，基础分设为0")
            else:
                base_score = config_data.get('base_score', 60)
                logger.info(f"基础条件满足，基础分为: {base_score}")
            
            # 将配置ID保存到结果中
            score_config_id = getattr(config, 'id', None)
            
            # 计算各项得分
            academic_score = ScoreService.calculate_academic_score(student, config)
            
            scholarship_result = ScoreService.calculate_scholarship_score(student, config)
            scholarship_score = scholarship_result['total_score']
            
            volunteer_result = ScoreService.calculate_volunteer_score(student, config)
            volunteer_score = volunteer_result['score']
            
            english_result = ScoreService.calculate_english_score(student, config)
            english_score = english_result['total_score']
            
            logger.info(f"各项得分: 学业={academic_score}, 奖学金={scholarship_score}, 志愿服务={volunteer_score}, 英语能力={english_score}")
            
            # 计算总分
            if passed_base_conditions:
                total_score = (
                    base_score +
                    academic_score +
                    scholarship_score +
                    volunteer_score +
                    english_score
                )
                logger.info(f"总分: {total_score}")
            else:
                # 基础条件不满足，总分为0
                total_score = 0
                logger.info("基础条件不满足，总分为0")
            
            # 返回评分结果
            return {
                'score_config_id': score_config_id,
                'total_score': total_score,
                'base_score': base_score,
                'academic_score': academic_score,
                'scholarship_score': scholarship_score,
                'volunteer_score': volunteer_score,
                'english_score': english_score,
                'base_conditions': base_conditions['base_conditions'],
                'passed_base_conditions': passed_base_conditions,
                'academic_result': {
                    'comprehensive_score': getattr(student, 'comprehensive_test_score', 0),
                    'weight': config_data.get('academic_weight', 0.15),
                    'score': academic_score
                },
                'scholarship_result': scholarship_result,
                'volunteer_result': volunteer_result,
                'english_result': english_result
            }
        except ValueError as e:
            # 数据完整性错误
            logger.error(f"计算总分时出错 (数据不完整): {str(e)}")
            raise
        except Exception as e:
            logger.error(f"计算总分时出错: {str(e)}")
            raise
    
    @staticmethod
    def save_student_score(student, score_result, user_id=None, remark=None):
        """保存学生评分结果"""
        # 创建评分记录
        student_score = StudentScore(
            student_id=student.student_id,
            score_config_id=score_result.get('score_config_id'),
            base_score=score_result.get('base_score', 0),
            academic_score=score_result.get('academic_score', 0),
            scholarship_score=score_result.get('scholarship_score', 0),
            volunteer_score=score_result.get('volunteer_score', 0),
            english_score=score_result.get('english_score', 0),
            total_score=score_result.get('total_score', 0),
            passed_base_conditions=score_result.get('passed_base_conditions', False),
            remark=remark,
            created_by=user_id
        )
        
        # 保存评分详情
        student_score.score_detail = score_result
        
        # 添加到数据库
        db.session.add(student_score)
        
        # 获取总分并确保它是数值
        total_score = score_result.get('total_score', 0)
        if isinstance(total_score, dict):
            if 'score' in total_score:
                total_score = total_score['score']
            elif 'total_score' in total_score:
                total_score = total_score['total_score']
            else:
                total_score = 0
                
        # 更新学生综合评分（不是综测成绩）
        student.comprehensive_score = round(float(total_score))
        
        # 提交更改
        try:
            db.session.commit()
            return True, student_score
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存学生评分出错: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def batch_calculate_scores(student_ids=None, config=None, user_id=None, update_student=True, remark=None):
        """批量计算多个学生的评分"""
        results = []
        
        try:
            # 查询学生
            query = Student.query
            if student_ids:
                logger.info(f"使用以下学生ID进行计算: {student_ids}")
                query = query.filter(Student.student_id.in_(student_ids))
            
            students = query.all()
            logger.info(f"准备为 {len(students)} 名学生计算评分")
            
            # 获取默认配置
            if config is None:
                config = ScoreConfig.get_default_config()
                logger.info(f"使用默认配置: {config.id}")
            else:
                logger.info(f"使用指定配置: {config.id}")
            
            # 对比查找到的学生与请求的学生ID
            if student_ids:
                found_ids = [s.student_id for s in students]
                logger.info(f"找到的学生ID: {found_ids}")
                missing_ids = set(student_ids) - set(found_ids)
                if missing_ids:
                    logger.warning(f"未找到以下学生ID: {missing_ids}")
            
            # 为每个学生计算评分
            for student in students:
                try:
                    # 记录要处理的学生信息
                    logger.info(f"开始处理学生: {student.student_id} ({student.name})")
                    
                    # 记录学生的关键字段值
                    logger.info(f"学生字段值: has_application={student.has_application}, " +
                                f"passed_exam={student.passed_exam}, " +
                                f"class_approved={student.class_approved}, " +
                                f"has_failed_course={student.has_failed_course}, " +
                                f"comprehensive_test_score={student.comprehensive_test_score}, " +
                                f"volunteer_hours={student.volunteer_hours}")
                    
                    # 检查学生数据完整性
                    missing_fields = []
                    required_fields = [
                        ("comprehensive_test_score", "综合测评成绩"), 
                        ("volunteer_hours", "志愿服务时长"),
                        ("has_application", "是否递交入党申请书"),
                        ("passed_exam", "是否通过党课考试"),
                        ("class_approved", "是否通过班级推优"),
                        ("has_failed_course", "是否有挂科记录")
                    ]
                    
                    for field, desc in required_fields:
                        # 因为布尔值可能是False，所以我们只检查它是否为None
                        attr_value = getattr(student, field, None)
                        if attr_value is None:
                            missing_fields.append(f"{field} ({desc})")
                    
                    if missing_fields:
                        error_msg = f"学生 {student.student_id} 数据不完整，缺少: {', '.join(missing_fields)}"
                        logger.error(error_msg)
                        results.append({
                            'student_id': student.student_id,
                            'name': student.name,
                            'success': False,
                            'error': error_msg
                        })
                        continue
                    
                    # 计算评分
                    try:
                        score_result = ScoreService.calculate_total_score(student, config)
                    except ValueError as e:
                        error_msg = f"学生 {student.student_id} 数据无法计算评分: {str(e)}"
                        logger.error(error_msg)
                        results.append({
                            'student_id': student.student_id,
                            'name': student.name,
                            'success': False,
                            'error': error_msg
                        })
                        continue
                    
                    # 保存评分结果
                    if update_student:
                        success, record = ScoreService.save_student_score(student, score_result, user_id, remark)
                        if success:
                            logger.info(f"学生 {student.student_id} 评分成功: {score_result.get('total_score')}分")
                        else:
                            logger.error(f"学生 {student.student_id} 评分保存失败: {record}")
                            
                        results.append({
                            'student_id': student.student_id,
                            'name': student.name,
                            'success': success,
                            'score': score_result.get('total_score'),
                            'details': score_result,
                            'error': None if success else str(record)
                        })
                    else:
                        # 不保存，只返回计算结果
                        results.append({
                            'student_id': student.student_id,
                            'name': student.name,
                            'success': True,
                            'score': score_result.get('total_score'),
                            'details': score_result
                        })
                except ValueError as e:
                    # 数据完整性错误
                    logger.error(f"学生 {student.student_id} 评分计算出错 (数据不完整): {str(e)}")
                    results.append({
                        'student_id': student.student_id,
                        'name': getattr(student, 'name', 'Unknown'),
                        'success': False,
                        'error': f"数据不完整: {str(e)}"
                    })
                except Exception as e:
                    logger.error(f"学生 {student.student_id} 评分计算出错: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    results.append({
                        'student_id': student.student_id,
                        'name': getattr(student, 'name', 'Unknown'),
                        'success': False,
                        'error': str(e)
                    })
            
            # 提交所有更改
            if update_student:
                try:
                    db.session.commit()
                    logger.info("批量评分完成，所有更改已提交")
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"批量评分提交时出错: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            return results
        except Exception as e:
            logger.error(f"批量计算评分过程中出现未预期错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return [] 