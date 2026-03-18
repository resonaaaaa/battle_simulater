import random

class Character:
    def __init__(self, name, level,maxHP,attack, defense):
        self.name = name
        self.level = 1
        self.maxHP = maxHP
        self.health = maxHP
        self.attack = attack
        self.defense = defense
        
        # 默认拥有基础攻击技能
        self.skills = {"attack": self.attack_target}
        self.skill_descriptions = {"attack": "普通攻击，造成基于攻击与目标防御计算的物理伤害。"}

        # 通用控制/减益状态
        """冻结"""
        self.skip_turn = False 
        self.frozen_turns = 0
        """攻击力下降"""
        self.attack_down_turns = 0
        self.attack_down_value = 0
        self.attack_down_source = ""
        """防御力下降"""
        self.defense_down_turns = 0
        self.defense_down_value = 0
        self.defense_down_source = ""
        """持续伤害"""
        self.continuous_damage_turns = 0
        self.continuous_damage_value = 0
        self.continuous_damage_source = ""
        """无法回复"""
        self.reheal_limit = False
        self.reheal_limit_turns = 0

        # 仅基础 Character 在这里直接补齐等级；子类会在各自 __init__ 末尾处理
        if self.__class__ is Character and level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
    
    def attack_target(self, target):
        damage = self.attack * 46 // (100 + target.defense*0.8)  
        if damage < 0:
            damage = 0
        print(f"{self.name} 攻击了 {target.name}，造成 {damage} 点伤害！")
        self.deal_damage(target, damage)

    def is_alive(self):
        return self.health > 0

    def on_turn_start(self):
        """每当该角色行动回合开始时触发。子类可重写以处理回合型效果。"""
        self.skip_turn = False

        #通用持续伤害结算
        if self.continuous_damage_turns > 0 and self.continuous_damage_value > 0:
            source_name = self.continuous_damage_source.name if self.continuous_damage_source is not None else "持续伤害"
            print(f"{self.name} 受到了 {source_name} 的持续伤害！")
            self.take_damage(self.continuous_damage_value, attacker=self.continuous_damage_source, attack_type="continuous")
            self.continuous_damage_turns -= 1
            if self.continuous_damage_turns <= 0:
                self.continuous_damage_value = 0
                self.continuous_damage_source = ""
            

        #攻击力下降
        if self.attack_down_turns > 0:
            self.attack_down_turns -= 1
            if self.attack_down_turns <= 0 and self.attack_down_value > 0:
                self.attack += self.attack_down_value
                print(f"{self.name} 的攻击抑制效果结束，攻击力恢复了 {self.attack_down_value} 点！")
                self.attack_down_value = 0
                self.attack_down_source = ""

        #防御力下降
        if self.defense_down_turns > 0:
            self.defense_down_turns -= 1
            if self.defense_down_turns <= 0 and self.defense_down_value > 0:
                self.defense += self.defense_down_value
                print(f"{self.name} 的防御抑制效果结束，防御力恢复了 {self.defense_down_value} 点！")
                self.defense_down_value = 0
                self.defense_down_source = ""

        #无法回复
        if self.reheal_limit_turns > 0:
            self.reheal_limit_turns -= 1
            if self.reheal_limit_turns <= 0:
                self.reheal_limit = False
                print(f"{self.name} 的无法回复效果结束，可以恢复生命值了！")

        # 冻结：冻结期间无法行动
        if self.frozen_turns > 0:
            print(f"{self.name} 无法行动！")
            self.frozen_turns -= 1
            self.skip_turn = True

    def can_act(self):
        return not self.skip_turn
    
    def level_up(self, announce=True):
        self.level += 1
        if announce:
            print(f"{self.name} 升到了 {self.level} 级！")

    def gain_levels(self, levels, announce=True):
        """连续提升指定等级。"""
        if levels <= 0:
            return
        for _ in range(levels):
            self.level_up(announce=announce)

    def deal_damage(self, target, value, attack_type="physical"):
        return target.take_damage(value, attacker=self, attack_type=attack_type)

    def take_damage(self, value,attacker = None,attack_type = "physical"):
        value = int(max(0, self.before_take_damage(value, attacker, attack_type)))
        if value == 0:
            return 0
        self.health -= value
        if self.health < 0:
            self.health = 0
        print(f"{self.name} 受到了 {value} 点伤害！当前生命值：{self.health}")
        self.after_take_damage(value, attacker, attack_type)
        return value

    def before_take_damage(self, value, attacker, attack_type):
        """在受到伤害前的处理，返回可能修改后的伤害值。子类可重写此方法实现特殊效果。"""
        return value
    
    def after_take_damage(self, value, attacker, attack_type):
        """在受到伤害后的处理，子类可重写此方法实现特殊效果。"""
        pass
        
    def health_regeneration(self,value):
        if self.reheal_limit:
            print(f"{self.name} 目前无法回复生命值！")
            return
        actual_value = min(value, self.maxHP - self.health)
        self.health += actual_value
        print(f"{self.name} 恢复了 {actual_value} 点生命值！当前生命值：{self.health}")

    def settlement(self):
        self.health = self.maxHP
        self.clear_debuffs(silent=True)
        self.skip_turn = False

    def clear_debuffs(self, silent=False):
        """清除通用debuff，并回滚由debuff带来的属性变化。"""
        self.frozen_turns = 0
        if self.attack_down_value > 0:
            self.attack += self.attack_down_value
        if self.defense_down_value > 0:
            self.defense += self.defense_down_value

        self.attack_down_turns = 0
        self.attack_down_value = 0
        self.attack_down_source = ""
        self.defense_down_turns = 0
        self.defense_down_value = 0
        self.defense_down_source = ""
        self.continuous_damage_turns = 0
        self.continuous_damage_value = 0
        self.continuous_damage_source = ""
        self.reheal_limit = False
        self.reheal_limit_turns = 0
        if not silent:
            print(f"{self.name} 身上的负面状态已被清除。")

    def apply_freeze(self, turns=1, source=None, type_name=''):
        turns = int(max(0, turns))
        if turns <= 0:
            return
        self.frozen_turns = max(self.frozen_turns, turns)
        if source is None:
            source_name = "未知"
        elif hasattr(source, "name"):
            source_name = source.name
        else:
            source_name = str(source)

        if type_name == "numbness":
            print(f"{self.name} 被 {source_name} 麻痹了 {turns} 回合！")
        elif type_name == 'freeze':
            print(f"{self.name} 被 {source_name} 冻结了 {turns} 回合！")
        else:
            print(f"{self.name} 因 {source_name} 而无法行动 {turns} 回合！")

    def apply_attack_down(self, ratio, turns, source_name=""):
        turns = int(max(0, turns))
        ratio = max(0.0, float(ratio))
        if turns <= 0 or ratio <= 0:
            return
        # 先撤销旧攻击降低，再按当前攻击重新计算，避免叠减失真
        if self.attack_down_value > 0:
            self.attack += self.attack_down_value

        down_value = int(max(1, self.attack * ratio))
        down_value = min(down_value, max(0, self.attack - 1))
        self.attack -= down_value
        self.attack_down_value = down_value
        self.attack_down_turns = turns
        self.attack_down_source = source_name
        print(f"{self.name} 的攻击被压制，降低了 {down_value} 点，持续 {turns} 回合！")

    def apply_defense_down(self, ratio, turns, source_name=""):
        turns = int(max(0, turns))
        ratio = max(0.0, float(ratio))
        if turns <= 0 or ratio <= 0:
            return
        # defense_down 通常在受击后附加，为避免在目标下个回合开始就提前损耗，内部额外补 1 回合
        effective_turns = turns + 1
        # 先撤销旧防御降低，再按当前防御重新计算，避免叠减失真
        if self.defense_down_value > 0:
            self.defense += self.defense_down_value

        down_value = int(max(1, self.defense * ratio))
        down_value = min(down_value, max(0, self.defense - 1))
        self.defense -= down_value
        self.defense_down_value = down_value
        self.defense_down_turns = effective_turns
        self.defense_down_source = source_name
        print(f"{self.name} 的防御被压制，降低了 {down_value} 点，持续 {turns} 回合！")

    def apply_continuous_damage(self, value, turns, source=None):
        value = int(max(0, value))
        turns = int(max(0, turns))
        if value <= 0 or turns <= 0:
            return
        self.continuous_damage_value = value
        self.continuous_damage_turns = turns
        self.continuous_damage_source = source
        source_name = source.name if source is not None else "未知来源"
        print(f"{self.name} 受到了 {source_name} 的持续伤害效果，每回合 {value} 点，持续 {turns} 回合！")

    # 通用技能接口 ------------------------------------------------
    def is_skill_available(self, skill_name):
        """判断技能当前是否可用。子类可重写该方法实现资源/状态判断。"""
        return skill_name in self.skills

    def get_available_skills(self):
        """返回当前可用技能列表。"""
        return [name for name in self.skills if self.is_skill_available(name)]

    def use_skill(self, skill_name, *args, **kwargs):
        """
        通过技能名称调用对应的技能函数，技能函数可以接受任意参数。
        这个方法提供了一个统一的接口来使用角色的技能，无论技能的具体实现如何。
        """
        skill = self.skills.get(skill_name)
        if skill is None:
            raise ValueError(f"{self.name} 不会技能 '{skill_name}'")
        if not self.is_skill_available(skill_name):
            raise ValueError(f"技能 '{skill_name}' 当前不可用")
        return skill(*args, **kwargs)

    def learn_skill(self, skill_name, func, description=None):
        self.skills[skill_name] = func
        if description:
            self.skill_descriptions[skill_name] = description

    def get_skill_descriptions(self):
        return dict(self.skill_descriptions)

    def get_runtime_status(self):
        """统一状态接口：返回当前 buff/debuff 与技能可用性信息。"""
        buffs = []
        debuffs = []
        if self.frozen_turns > 0:
            debuffs.append(f"frozen({self.frozen_turns})")
        if self.attack_down_turns > 0 and self.attack_down_value > 0:
            debuffs.append(f"atk_down(-{self.attack_down_value}, {self.attack_down_turns})")
        if self.defense_down_turns > 0 and self.defense_down_value > 0:
            debuffs.append(f"def_down(-{self.defense_down_value}, {self.defense_down_turns})")
        if self.continuous_damage_turns > 0 and self.continuous_damage_value > 0:
            debuffs.append(f"cont_dmg({self.continuous_damage_value}, {self.continuous_damage_turns})")
        if self.reheal_limit and self.reheal_limit_turns > 0:
            debuffs.append(f"no_heal({self.reheal_limit_turns})")
        return {
            "buffs": buffs,
            "debuffs": debuffs,
            "skill_runtime": self.get_skill_runtime_info(),
        }

    def get_skill_runtime_info(self):
        """统一技能运行时信息接口，子类可覆盖返回冷却/次数等。"""
        return {}

class Berserker(Character):
    def __init__(self, name, level = 1, maxHP = 220, attack = 100, defense = 20):
        super().__init__(name, level, maxHP, attack, defense)
        self.rage = 0
        self.rage_flag = False
        self.rage_buff_turns = 0
        self.unleash_rage_threshold = 20
        self.crazy_strike_cooldown = 0
        self.learn_skill("get_into_anger", self.get_into_anger, "消耗50点怒气进入狂怒，提升攻击并降低防御，持续3次自身行动回合。")
        self.learn_skill("unleash_rage", self.unleash_rage, "狂怒状态下消耗至少20点怒气释放怒焰，造成高额伤害。")
        self.learn_skill("crazy_strike", self.crazy_strike, "消耗20点怒气，对敌人造成部分穿透防御的伤害，并有概率使敌人防御力下降2回合，冷却4回合。有20%概率造成暴击。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.rage = 0
            self.rage_flag = False

    def is_skill_available(self, skill_name):
        if skill_name == "get_into_anger":
            return (not self.rage_flag) and self.rage >= 50
        if skill_name == "unleash_rage":
            return self.rage_flag and self.rage >= self.unleash_rage_threshold 
        if skill_name == "crazy_strike":
            return self.crazy_strike_cooldown <= 0 and self.rage >= 20
        return super().is_skill_available(skill_name)
    
    def on_turn_start(self):
        super().on_turn_start()
        if self.rage_flag:
            self.rage_buff_turns -= 1
            if self.rage_buff_turns <= 0:
                self.attack = int(self.attack / 1.5)
                self.defense = int(self.defense / 0.7)
                self.rage_flag = False
                print(f"{self.name} 的狂怒效果结束，攻击和防御恢复正常！")
        if self.crazy_strike_cooldown > 0:
            self.crazy_strike_cooldown -= 1


    def attack_target(self, target):
        super().attack_target(target)
        self.rage += 12

    def after_take_damage(self, value, attacker, attack_type):
        self.rage += 8
        if self.rage > 100:
            self.rage = 100

    def get_into_anger(self):
        if self.rage >= 50:
            self.attack = int(self.attack * 1.5)
            self.defense = int(self.defense * 0.7)
            print(f"{self.name} 进入狂怒！攻击提高，但防御下降！")
            self.rage -= 50
            self.rage_flag = True
            # 狂怒回合在回合开始时递减，这里补 1 以保证可完整行动 3 次
            self.rage_buff_turns = 4
        else:
            print(f"{self.name} 怒气不足，无法进入狂怒状态！")

    def crazy_strike(self, target):
        if self.rage < 20:
            print(f"{self.name} 怒气不足，无法使用狂暴重击！")
            return
        damage = int(self.attack * 0.4) // (1 + target.defense*0.6/100)
        if damage < 0:
            damage = 0
        if random.random() < 0.2:
            damage = int(damage * 1.5)
            print(f"{self.name} 的狂暴重击触发了暴击！伤害大幅提升！")
        print(f"{self.name} 使用了狂暴重击，对 {target.name} 造成 {damage} 点伤害！")
        self.deal_damage(target, damage)
        self.rage -= 20
        # 50%概率使敌人防御力下降，持续2回合
        if random.random() < 0.5:
            target.apply_defense_down(ratio=0.20, turns=2, source_name="狂暴重击")
        self.crazy_strike_cooldown = 4

    def unleash_rage(self, target):
        if self.rage_flag and self.rage >= self.unleash_rage_threshold:
            damage = int(self.attack * 0.3 + 2 * self.rage) // (1 + target.defense*0.8/100)  # 狂怒释放伤害根据当前攻击力和怒气值计算
            self.rage = 0
            self.rage_flag = False
            if damage < 0:
                damage = 0
            print(f"{self.name} 对 {target.name} 释放怒焰，造成 {damage} 点伤害！")
            self.deal_damage(target, damage)
        else:
            print(f"{self.name} 怒气不足或未进入狂怒状态，无法释放怒焰！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 16
        self.attack += 11
        self.defense += 4
    
    def settlement(self):
        if self.rage_flag:
            self.attack = int(self.attack / 1.5)
            self.defense = int(self.defense / 0.7)
        super().settlement()
        self.rage = 0
        self.rage_flag = False

    def get_runtime_status(self):
        data = super().get_runtime_status()
        if self.rage_flag:
            data["buffs"].append(f"rage({self.rage_buff_turns})")
        return data

    def get_skill_runtime_info(self):
        return {
            "crazy_strike": f"cd={self.crazy_strike_cooldown}",
        }

class Vampire(Character):
    def __init__(self, name, level = 1, maxHP = 210, attack = 90, defense = 15):
        super().__init__(name, level, maxHP, attack, defense)
        self.blood_sucking_level = 1 + (level - 1) // 5
        self.bat_count = 0
        self.learn_skill("bat_summon", self.bat_summon, "召唤蝙蝠（上限3只），为普攻提供额外伤害，蝙蝠的攻击部分穿透防御。")
        self.learn_skill("bat_bomb", self.bat_bomb, "引爆全部蝙蝠造成高爆发伤害，蝙蝠越多，伤害越高。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.bat_count = 0

    def is_skill_available(self, skill_name):
        if skill_name == "bat_summon":
            return self.bat_count < 3
        if skill_name == "bat_bomb":
            return self.bat_count > 1
        return super().is_skill_available(skill_name)

    def attack_target(self, target):
        damage = (self.attack * 40) // (100 + target.defense*0.8)
        print(f"{self.name} 攻击了 {target.name}，造成 {damage} 点伤害！")
        bat_damage = (self.bat_count * self.attack * 0.1) * 40 // (100 + target.defense*0.6) # 每只蝙蝠增加10%攻击力的伤害，且略微穿透防御
        print(f"{self.name} 的蝙蝠追加了 {bat_damage} 点伤害！")
        damage += int(bat_damage)
        if damage < 0:
            damage = 0
        actual_damage = self.deal_damage(target, damage)
        if actual_damage > 0:
            blood_sucked = int(actual_damage * 0.35) + 15 + int(self.blood_sucking_level * 2)
            print(f"{self.name} 吸血恢复了 {blood_sucked} 点生命值!")
            self.health_regeneration(blood_sucked)


    def bat_summon(self):
        if self.bat_count < 3:
            self.bat_count += 1 
            print(f"{self.name} 召唤了一只蝙蝠！当前蝙蝠数量：{self.bat_count}") 
        else:
            print(f"{self.name} 的蝙蝠数量已达到上限！")
    
    def bat_bomb(self, target):
        if self.bat_count > 1:
            damage = int((self.bat_count * self.attack * 0.35) // (1 + target.defense*0.80/100)) + 12 * self.bat_count  # 每只蝙蝠造成45%攻击力的伤害，且穿透防御，外加每只蝙蝠12点固定伤害
            print(f"{self.name} 引爆了 {self.bat_count} 只蝙蝠，对 {target.name} 造成 {damage} 点伤害！")
            self.deal_damage(target,value=damage, attack_type="magical")
            self.bat_count = 0
        else:
            print(f"{self.name} 没有足够多的蝙蝠可用来引爆！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 15
        self.attack += 11
        self.defense += 4

    def settlement(self):
        super().settlement()
        self.bat_count = 0

class Knight(Character):
    def __init__(self, name, level = 1, maxHP = 280, attack = 70, defense = 30):
        super().__init__(name, level, maxHP, attack, defense)
        self.sacred_crash_flag = False
        self.counterattack_active = False
        self.counterattack_active_turns = 0
        self.counterattack_damage_ratio = 0.6
        self.counterattack_cooldown = 0
        self.learn_skill("counterattack", self.counterattack, "进入反击架势：下一次受到物理伤害时完全格挡并反击60%的伤害。")
        self.learn_skill("sacred_crash", self.sacred_crash, "神圣冲击：根据已损生命值提高伤害。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP

    def is_skill_available(self, skill_name):
        if skill_name == "counterattack":
            return (not self.counterattack_active) and self.counterattack_cooldown == 0
        if skill_name == "sacred_crash":
            return not self.sacred_crash_flag
        return super().is_skill_available(skill_name)

    def on_turn_start(self):
        super().on_turn_start()
        if self.counterattack_cooldown > 0:
            self.counterattack_cooldown -= 1
        if self.counterattack_active:
            self.counterattack_active_turns -= 1
            if self.counterattack_active_turns <= 0:
                self.counterattack_active = False
                print(f"{self.name} 的反击架势结束了。")

    def attack_target(self, target):
        super().attack_target(target)

    def before_take_damage(self, value, attacker, attack_type):
        if attack_type == "physical" and attacker is not None and self.counterattack_active:
            counter_damage = int(value * self.counterattack_damage_ratio)
            print(f"{self.name} 成功格挡了攻击，并反击了 {attacker.name}，造成 {counter_damage} 点伤害！")
            self.deal_damage(attacker, counter_damage, attack_type="counterattack")
            self.counterattack_active = False
            self.counterattack_active_turns = 0
            return 0
        return value

    def sacred_crash(self, target):
        if self.sacred_crash_flag:
            print(f"{self.name} 已经使用过神圣冲击了，无法再次使用！")
            return
        damage = int(self.attack * 0.4 )// (1 + target.defense*0.8/100) + min(200,(self.maxHP - self.health)*0.25)  # 自身损失血量越多，伤害越高,最多增加200点伤害
        if damage < 0:
            damage = 0
        print(f"{self.name} 施放神圣冲击，对 {target.name} 造成 {damage} 点伤害！")
        self.deal_damage(target, damage)
        self.sacred_crash_flag = True

    def counterattack(self):
        if self.counterattack_active:
            print(f"{self.name} 已经处于反击架势中！")
            return
        if self.counterattack_cooldown > 0:
            print(f"{self.name} 的反击仍在冷却中，还需 {self.counterattack_cooldown} 回合！")
            return
        self.counterattack_active = True
        self.counterattack_active_turns = 1
        self.counterattack_cooldown = 3
        print(f"{self.name} 进入反击架势，准备格挡下一次物理攻击！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 18
        self.attack += 8
        self.defense += 6

    def settlement(self):
        super().settlement()
        self.counterattack_active = False
        self.counterattack_active_turns = 0
        self.counterattack_cooldown = 0

    def get_runtime_status(self):
        data = super().get_runtime_status()
        if self.counterattack_active:
            data["buffs"].append(f"counter_stance({self.counterattack_active_turns})")
        return data

    def get_skill_runtime_info(self):
        return {
            "counterattack": f"cd={self.counterattack_cooldown}",
            "sacred_crash": f"remaining={0 if self.sacred_crash_flag else 1}",
        }


class DragonHuman(Character):
    def __init__(self, name, level= 1, maxHP = 240, attack = 90, defense = 25):
        super().__init__(name, level, maxHP, attack, defense)
        self.dragon_breath = 0
        self.max_dragon_breath = 50
        self.attack_buff_flag = False
        self.attack_buff_turns = 0
        self.learn_skill("dragon_breath_attack", self.dragon_breath_attack, "消耗所有龙息释放强化攻击，并获得2回合攻击提升。")
        self.learn_skill("dragon_flame", self.dragon_flame, "消耗所有龙息释放龙焰，对目标造成最大生命值百分比伤害，并附加2回合的龙炎效果，造成持续伤害并无法回血。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.dragon_breath = 0

    def is_skill_available(self, skill_name):
        if skill_name == "dragon_breath_attack":
            return self.dragon_breath >= 30
        if skill_name == "dragon_flame":
            return self.dragon_breath >= 50
        return super().is_skill_available(skill_name)
    
    def on_turn_start(self):
        super().on_turn_start()
        if self.attack_buff_flag:
            self.attack_buff_turns -= 1
            if self.attack_buff_turns <= 0:
                self.attack = int(self.attack / 1.2)  # 恢复原始攻击力
                self.attack_buff_flag = False
                print(f"{self.name} 的龙息攻击效果结束，攻击力恢复正常！")

    def attack_target(self, target):
        super().attack_target(target)
        self.dragon_breath += 10
        if self.dragon_breath > self.max_dragon_breath:
            self.dragon_breath = self.max_dragon_breath
    
    def dragon_flame(self,target):
        if self.dragon_breath >= 50:
            damage = min(240,target.maxHP * 0.16)   #对敌人造成敌人最大生命值16%，最多240点伤害
            damage = int(damage)
            self.dragon_breath = 0
            print(f"{self.name} 释放龙焰，对 {target.name} 造成 {damage} 点伤害！")
            self.deal_damage(target, damage, attack_type="magical")
            target.apply_continuous_damage(value=min(40, int(target.health * 0.10)), turns=2, source=self)  # 每回合造成敌人当前生命值10%的伤害，最多40点，并且无法回血
            target.reheal_limit = True
            target.reheal_limit_turns = 2
        else:
            print("龙息值不足，无法释放龙焰！")

    #龙息攻击，伤害根据龙息值和等级提升，可以部分穿透目标防御，且短暂提高自身的攻击力,持续2回合
    def dragon_breath_attack(self,target):
        if self.dragon_breath >= 30:
            growth = 1 + min(self.level, 20) * 0.06 + max(0, self.level - 20) * 0.01
            damage = self.dragon_breath * growth // (1 + target.defense*0.5/100)
            self.dragon_breath = 0
            damage = int(damage)
            print(f"{self.name} 释放龙息，对 {target.name} 造成 {damage} 点伤害！")
            if not self.attack_buff_flag:
                self.attack = int(self.attack * 1.2)  # 暂时提高攻击力
                self.attack_buff_flag = True
            # 由于在回合开始递减计数，这里补 1，确保体感为 2 次自身行动回合
            self.attack_buff_turns = 3
            self.deal_damage(target, damage, attack_type="magical")
        else:
            print("龙息值不足，无法释放龙息攻击！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 16
        self.attack += 10
        self.defense += 5
        self.max_dragon_breath += 1
    
    def settlement(self):
        super().settlement()
        self.dragon_breath = 0

    def get_skill_runtime_info(self):
        return {}

class FlameWitch(Character):
    def __init__(self, name, level = 1, maxHP = 195, attack = 100, defense = 10):
        super().__init__(name, level, maxHP, attack, defense)
        self.maxMP = 60
        self.MP = self.maxMP
        self.shield = 0
        self.learn_skill("flame_crash", self.flame_crash, "消耗法力施放爆炎冲击，造成无视防御的魔法伤害,且附带灼烧效果，3回合内造成持续伤害并降低攻击力")
        self.learn_skill("flame_shield", self.flame_shield, "消耗法力生成烈焰护盾，护盾破裂时反弹部分伤害。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.MP = self.maxMP
            self.shield = 0

    def is_skill_available(self, skill_name):
        if skill_name in {"flame_crash", "flame_shield"}:
            return self.MP >= 25
        return super().is_skill_available(skill_name)

    def flame_crash(self,target):
        if self.MP < 25:
            print(f"{self.name} 法力不足，无法施放爆炎冲击！")
            return
        self.MP -= 25
        
        crash_damage = int(self.attack * 0.16 + 32)
        print(f"{self.name} 施放爆炎冲击，对 {target.name} 造成 {crash_damage} 点伤害！")
        self.deal_damage(target, crash_damage, attack_type="magical")
        if target.continuous_damage_turns == 0:  # 如果目标没有持续伤害效果，则施加新的灼烧效果
            target.apply_continuous_damage(value=min(24, int(target.health * 0.07)), turns=3, source=self)  # 每回合造成敌人当前生命值7%的伤害，最多24点
            target.apply_attack_down(ratio=0.08, turns=3, source_name="灼烧")  # 降低敌人8%攻击力，持续3回合
        else:
            print(f"{target.name} 已经有灼烧效果了，无法再次施加灼烧效果！")
    
    def flame_shield(self):
        if self.MP < 25:
            print(f"{self.name} 法力不足，无法施放烈焰护盾！")
            return
        self.MP -= 25
        self.shield = min(int(self.maxHP * 0.06 + 28), 80)
        print(f"{self.name} 施放烈焰护盾，获得 {self.shield} 点护盾值！")
    
    def before_take_damage(self, value, attacker, attack_type):
        if self.shield > 0:
            if attack_type != "counterattack": 
                blocked = min(self.shield, value)
                self.shield -= blocked
                remain = value - blocked
                print(f"{self.name} 的烈焰护盾吸收了 {blocked} 点伤害，剩余护盾：{self.shield}")
                    
                if self.shield == 0 and attacker is not None:
                    bounce = int(blocked * 0.3)
                    if bounce > 0:
                        print(f"{self.name} 的烈焰护盾被打破了，反弹了 {bounce} 点伤害给 {attacker.name}！")
                        self.deal_damage(attacker, bounce, attack_type="counterattack")  # 护盾被打破时反弹伤害
                return remain
        return value

    def get_skill_runtime_info(self):
        return {}

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxMP += 2
        self.attack += 11
        self.defense += 4
        self.maxHP += 14

    def settlement(self):
        super().settlement()
        self.MP = self.maxMP
        self.shield = 0

class Mermaid(Character):
    def __init__(self, name, level = 1, maxHP = 240, attack = 75, defense = 30):
        super().__init__(name, level, maxHP, attack, defense)
        self.water_control_level = 1 + (level - 1) // 5
        self.shield = 0
        self.water_shield_cooldown = 0
        self.rapid_flow_cooldown = 0
        self.cure_song_cooldown = 0
        self.support_skill_uses = 2
        self.learn_skill("water_shield", self.water_shield, "生成水盾优先吸收伤害，冷却5回合。")
        self.learn_skill("cure_song", self.cure_song, "回复已损生命值的60%，最多180点，冷却5回合。与宁静波纹共享2次总次数。")
        self.learn_skill("peaceful_wave", self.peaceful_wave, "宁静波纹：消除所有debuff。与治愈歌谣共享2次总次数。")
        self.learn_skill("rapid_flow", self.rapid_flow, "激流：对敌人造成更高伤害并使其防御力显著下降，持续2回合，冷却4回合")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.shield = 0
            self.water_shield_cooldown = 0
            self.rapid_flow_cooldown = 0
            self.cure_song_cooldown = 0
            self.support_skill_uses = 2

    def water_shield(self):
        if self.water_shield_cooldown > 0:
            print(f"{self.name} 的水盾仍在冷却中，还需 {self.water_shield_cooldown} 回合！")
            return
    
        shield_value = int(24 + self.water_control_level * 7 + self.defense * 0.05)
        self.shield = min(95, shield_value)
        self.water_shield_cooldown = 5
        print(f"{self.name} 形成了水盾，获得 {self.shield} 点护盾值！")

    """宁静波纹：消除所有debuff，限用2次"""
    def peaceful_wave(self):
        if self.support_skill_uses > 0:
            self.clear_debuffs(silent=True)
            self.support_skill_uses -= 1
            print(f"{self.name} 发出了宁静波纹，所有debuff被消除了！共享剩余次数：{self.support_skill_uses}")
        else:
            print(f"治愈歌谣/宁静波纹的共享次数已用完！")

    def on_turn_start(self):
        super().on_turn_start()
        if self.water_shield_cooldown > 0:
            self.water_shield_cooldown -= 1
        if self.rapid_flow_cooldown > 0:
            self.rapid_flow_cooldown -= 1
    
    def before_take_damage(self, value, attacker, attack_type):
        if self.shield > 0:
            blocked = min(self.shield, value)
            self.shield -= blocked
            remain = value - blocked
            print(f"{self.name} 的水盾吸收了 {blocked} 点伤害，剩余护盾：{self.shield}")
            return remain
        return value

    #激流：对敌人造成伤害并使其防御力下降，持续2回合，冷却4回合
    def rapid_flow(self, target):
        if self.rapid_flow_cooldown > 0:
            print(f"{self.name} 的激流仍在冷却中，还需 {self.rapid_flow_cooldown} 回合！")
            return
        damage = int(self.attack * 0.30) // (1 + target.defense*0.8/100) + 4 * (self.water_control_level + 10)
        print(f"{self.name} 施放了激流，对 {target.name} 造成 {damage} 点伤害！")
        self.deal_damage(target, damage)
        target.apply_defense_down(ratio=0.25, turns=2, source_name="激流")
        self.rapid_flow_cooldown = 4
 
    def cure_song(self):
        if self.support_skill_uses > 0 and self.health < self.maxHP and self.cure_song_cooldown == 0:
            heal_value = int(min(180, (self.maxHP - self.health) * 0.6))
            self.health_regeneration(heal_value)  #回复已损失生命值的60%，最多180点
            self.support_skill_uses -= 1
            self.cure_song_cooldown = 5
            print(f"{self.name} 的歌声治愈动人！共享剩余次数：{self.support_skill_uses}")
        else:
            print(f"治愈歌谣/宁静波纹的共享次数已用完或正在冷却中！")

    def is_skill_available(self, skill_name):
        if skill_name == "water_shield":
            return self.water_shield_cooldown == 0
        if skill_name == "cure_song":
            return self.support_skill_uses > 0 and self.cure_song_cooldown == 0
        if skill_name == "peaceful_wave":
            return self.support_skill_uses > 0
        if skill_name == "rapid_flow":
            return self.rapid_flow_cooldown == 0
        return super().is_skill_available(skill_name)
    
    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 18
        self.attack += 8
        self.defense += 5
        self.water_control_level = 1 + (self.level - 1) // 5

    def settlement(self):
        super().settlement()
        self.shield = 0
        self.water_shield_cooldown = 0
        self.support_skill_uses = 2
        self.rapid_flow_cooldown = 0
    def get_skill_runtime_info(self):
        return {
            "water_shield": f"cd={self.water_shield_cooldown}",
            "cure_song": f"remaining={self.support_skill_uses} (shared)",
            "peaceful_wave": f"remaining={self.support_skill_uses} (shared)",
            "rapid_flow": f"cd={self.rapid_flow_cooldown}",
        }

class WolfMan(Character):
    def __init__(self, name, level = 1, maxHP = 235, attack = 85, defense = 25):
        super().__init__(name, level, maxHP, attack, defense)
        self.wolf_evolution_flag = False
        self.bloody_bite_cooldown = 0
        self.wolf_cry_cooldown = 0
        self.learn_skill("wolf_evolution", self.wolf_evolution, "生命值较低时可进入狼化形态，普攻更易穿透防御。")
        self.learn_skill("bloody_bite", self.bloody_bite, "造成伤害并在目标血量较高时吸血，冷却3回合。")
        self.learn_skill("wolf_cry", self.wolf_cry, "仅在狼人形态下可用，对敌人造成防御力与攻击力下降，持续2回合，冷却4回合。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.wolf_evolution_flag = False
            self.bloody_bite_cooldown = 0
            self.wolf_cry_cooldown = 0

    def is_skill_available(self, skill_name):
        if skill_name == "wolf_evolution":
            return self.health < self.maxHP * 0.5 and not self.wolf_evolution_flag
        if skill_name == "bloody_bite":
            return self.bloody_bite_cooldown == 0
        if skill_name == "wolf_cry":
            return self.wolf_evolution_flag and self.wolf_cry_cooldown == 0
        return super().is_skill_available(skill_name)

    def on_turn_start(self):
        super().on_turn_start()
        if self.bloody_bite_cooldown > 0:
            self.bloody_bite_cooldown -= 1
        if self.wolf_cry_cooldown > 0:
            self.wolf_cry_cooldown -= 1
    
    def wolf_evolution(self):
        if self.health < self.maxHP * 0.5 and self.wolf_evolution_flag == False:
            print(f"{self.name} 进入狼人形态！攻击将部分无视防御！")
            self.wolf_evolution_flag = True
        else:
            print(f"{self.name} 无法进入狼人形态！")

    """狼嚎：仅在狼人形态下可用，对敌人造成防御力与攻击力下降，持续2回合，冷却4回合"""
    def wolf_cry(self,target):
        if self.wolf_evolution_flag:
            print(f"{self.name} 发出了狼嚎，对 {target.name} 造成了恐怖！{target.name} 的攻击力和防御力下降了！")
            target.apply_attack_down(ratio=0.15, turns=2, source_name="狼嚎")
            target.apply_defense_down(ratio=0.25, turns=2, source_name="狼嚎")
            self.wolf_cry_cooldown = 4
        else:
            print(f"{self.name} 只有在狼人形态下才能使用狼嚎！")

    def attack_target(self, target):
        if self.wolf_evolution_flag == True:
            damage = self.attack * 45 // (100 + target.defense*0.4) + 10 # 狼人形态部分无视防御,且增加固定伤害
            print(f"{self.name} 狼化攻击了 {target.name}，造成 {int(damage)} 点伤害！")
            self.deal_damage(target, damage)
        else:
            super().attack_target(target)
    
    def bloody_bite(self,target):
        if self.bloody_bite_cooldown > 0:
            print(f"{self.name} 的血腥之咬仍在冷却中，还需 {self.bloody_bite_cooldown} 回合！")
            return
        damage = int(self.attack * 50 // (100 + target.defense*0.8))
        target_hp_ratio_before = target.health / target.maxHP if target.maxHP > 0 else 0
        actual_damage = self.deal_damage(target, damage)
        self.bloody_bite_cooldown = 3
        if target_hp_ratio_before > 0.4:
            if actual_damage > 0:
                bite_heal = int(actual_damage * 0.6)  # 吸取实际造成伤害的60%作为生命回复
                if bite_heal > 0:
                    print(f"{self.name} 使用血腥之咬，对 {target.name} 造成了 {actual_damage} 点伤害，并吸取了 {bite_heal} 点生命值！")
                    self.health_regeneration(bite_heal)
        else:
            print(f"{target.name}的生命值过低，无法吸取生命值！")


    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 16
        self.attack += 11
        self.defense += 4

    def settlement(self):
        super().settlement()
        self.wolf_evolution_flag = False
        self.bloody_bite_cooldown = 0
        self.wolf_cry_cooldown = 0

    def get_runtime_status(self):
        data = super().get_runtime_status()
        if self.wolf_evolution_flag:
            data["buffs"].append("wolf_form")
        return data

    def get_skill_runtime_info(self):
        return {
            "bloody_bite": f"cd={self.bloody_bite_cooldown}",
            "wolf_cry": f"cd={self.wolf_cry_cooldown}",
        }

class Druid(Character):
    def __init__(self, name, level = 1, maxHP = 205, attack = 85, defense = 15):
        super().__init__(name, level, maxHP, attack, defense)
        self.nature_summon_count = 0
        self.nature_summon_limit = 2
        self.summons = {'bear': False, 'eagle': False, 'treant': False, 'rabbit': False, 'deer': False}
        self.summons_on_field = []
        self.tree_spirit_blessing_turns = 0
        self.tree_spirit_blessing_cooldown = 0
        self.treant_max_hp = int(self.maxHP * 0.2)
        self.tree_spirit_blessing_active = False
        self.tree_spirit_blessing_defense_bonus = 0
        self.learn_skill("nature_summon", self.nature_summon, "随机召唤自然生物协助战斗，最多2个。")
        self.learn_skill("tree_spirit_blessing", self.tree_spirit_blessing, "提升防御3次自身行动回合。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.nature_summon_count = 0
            self.summons = {key: False for key in self.summons}
            self.summons_on_field = []
            self.tree_spirit_blessing_active = False
            self.tree_spirit_blessing_turns = 0
            self.tree_spirit_blessing_cooldown = 0
            self.tree_spirit_blessing_defense_bonus = 0
            self.treant_max_hp = int(self.maxHP * 0.2)

    def is_skill_available(self, skill_name):
        if skill_name == "nature_summon":
            return self.nature_summon_count < self.nature_summon_limit
        if skill_name == "tree_spirit_blessing":
            return (not self.tree_spirit_blessing_active) and self.tree_spirit_blessing_cooldown == 0
        return super().is_skill_available(skill_name)
    
    def nature_summon(self):
        if self.nature_summon_count >= self.nature_summon_limit:
            print(f"{self.name} 已经召唤了 {self.nature_summon_limit} 个自然生物，无法再召唤了！")
            return
        summon = random.choice(list(self.summons.keys()))
        while self.summons[summon]:  # 如果随机到的生物已经在场上了，就重新随机
            summon = random.choice(list(self.summons.keys()))
        self.summons[summon] = True
        self.nature_summon_count += 1
        self.summons_on_field.append(summon)
        if summon == 'treant':
            self.treant_max_hp = int(self.maxHP * 0.2)
        print(f"{self.name} 召唤了一个 {summon} 来协助战斗！当前召唤数量：{self.nature_summon_count}")

    def tree_spirit_blessing(self):
        if self.tree_spirit_blessing_active:
            print(f"{self.name} 已经受到了树灵的佑护，无法再次使用了！")
            return
        if self.tree_spirit_blessing_cooldown > 0:
            print(f"{self.name} 的树灵佑护仍在冷却中，还需 {self.tree_spirit_blessing_cooldown} 回合！")
            return
        self.tree_spirit_blessing_defense_bonus = int(self.defense * 0.3 + 48)
        self.defense += self.tree_spirit_blessing_defense_bonus
        self.tree_spirit_blessing_active = True
        self.tree_spirit_blessing_turns = 4
        self.tree_spirit_blessing_cooldown = 5
        print(f"{self.name} 受到了树灵的佑护，防御力暂时提高了 {self.tree_spirit_blessing_defense_bonus} 点！")

    def on_turn_start(self):
        super().on_turn_start()
        if self.tree_spirit_blessing_cooldown > 0:
            self.tree_spirit_blessing_cooldown -= 1
        if self.tree_spirit_blessing_active:
            self.tree_spirit_blessing_turns -= 1
            if self.tree_spirit_blessing_turns <= 0:
                self.defense -= self.tree_spirit_blessing_defense_bonus
                self.tree_spirit_blessing_defense_bonus = 0
                self.tree_spirit_blessing_active = False
                # 佑护结束时小幅回复
                self.health_regeneration(int(self.maxHP * 0.05 + self.level))
                print(f"{self.name} 的树灵佑护效果结束，防御力恢复正常！并回复了 {int(self.maxHP * 0.05 + self.level)} 点生命值！")
    
    def attack_target(self, target):
        damage = self.attack * 43 // (100 + target.defense*0.8)
        print(f"{self.name} 攻击了 {target.name}，造成 {damage} 点伤害！")
        if 'deer' in self.summons_on_field:
           if random.random() < 0.4:  # 40%概率回复生命值
                heal_value = int(self.health * 0.3) + 20  # 回复30%当前生命值 + 20点基础值
                self.health_regeneration(heal_value)
                print(f"{self.name} 的鹿帮助他回复了 {heal_value} 点生命值！")
        if 'bear' in self.summons_on_field:
            bear_damage = int((self.attack * 18) // (100 + target.defense*0.8)) + 8
            damage += bear_damage
            print(f"{self.name} 的熊造成了额外 {bear_damage} 点伤害！")
        if 'eagle' in self.summons_on_field:
            eagle_damage = int((self.attack * 9) // (100 + target.defense*0.8))
            if random.random() < 0.3:  # 30%概率暴击3倍伤害
                eagle_damage = 3 * eagle_damage
                print(f"{self.name} 的鹰触发了暴击！")
            damage += eagle_damage
            print(f"{self.name} 的鹰造成了额外 {eagle_damage} 点伤害！")
        
        self.deal_damage(target, damage)

    def before_take_damage(self, value, attacker, attack_type):
        if 'treant' in self.summons_on_field:
            treant_block = min(self.treant_max_hp, value)
            self.treant_max_hp -= treant_block
            remain = value - treant_block
            print(f"{self.name} 的树人代替他承受了 {treant_block} 点伤害，树人剩余生命值：{self.treant_max_hp}")
            if self.treant_max_hp <= 0:
                print(f"{self.name} 的树人被击败了！")
                self.summons['treant'] = False
                self.summons_on_field.remove('treant')
                self.nature_summon_count -= 1
            return remain
        if 'rabbit' in self.summons_on_field:
            if random.random() < 0.4:  # 40%概率闪避攻击
                print(f"{self.name} 的兔子帮助他闪避了攻击！")
                return 0  # 闪避成功，德鲁伊不受伤害
        return value
    
    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 14
        self.attack += 9
        self.defense += 4
        if 'treant' not in self.summons_on_field:
            self.treant_max_hp = int(self.maxHP * 0.2)

    def settlement(self):
        super().settlement()
        self.nature_summon_count = 0
        self.summons = {key: False for key in self.summons}
        self.summons_on_field = []
        if self.tree_spirit_blessing_active and self.tree_spirit_blessing_defense_bonus > 0:
            self.defense -= self.tree_spirit_blessing_defense_bonus
        self.tree_spirit_blessing_active = False
        self.tree_spirit_blessing_turns = 0
        self.tree_spirit_blessing_cooldown = 0
        self.tree_spirit_blessing_defense_bonus = 0
        self.treant_max_hp = int(self.maxHP * 0.2)

    def get_runtime_status(self):
        data = super().get_runtime_status()
        if self.tree_spirit_blessing_active:
            data["buffs"].append(f"tree_blessing({self.tree_spirit_blessing_turns})")
        if self.summons_on_field:
            data["buffs"].append("summons:" + ",".join(self.summons_on_field))
        return data

    def get_skill_runtime_info(self):
        return {
            "nature_summon": f"remaining={self.nature_summon_limit - self.nature_summon_count}",
            "tree_spirit_blessing": f"cd={self.tree_spirit_blessing_cooldown}",
        }

class SnowElf(Character):
    def __init__(self, name, level = 1, maxHP = 200, attack = 90, defense = 15):
        super().__init__(name, level, maxHP, attack, defense)
        self.ice_arrow_active_attacks = 0
        self.ice_arrow_cooldown = 0
        self.blizzard_used = False
        self.frost_spear_cooldown = 0
        self.learn_skill("ice_arrow", self.ice_arrow, "冰晶箭矢：强化接下来的2次普攻，伤害提高并有30%概率冻结目标1回合，冷却4回合。")
        self.learn_skill("blizzard", self.blizzard, "暴风雪：在场上召唤持续3回合的暴风雪，每回合对敌人造成伤害并降低其20%攻击力。每次战斗限1次。")
        self.learn_skill("frost_spear", self.frost_spear, "寒霜长矛：造成穿透部分防御的伤害，并有70%概率冻结目标1回合，冷却3回合。")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.ice_arrow_active_attacks = 0
            self.ice_arrow_cooldown = 0
            self.blizzard_used = False
            self.frost_spear_cooldown = 0

    def is_skill_available(self, skill_name):
        if skill_name == "ice_arrow":
            return self.ice_arrow_cooldown == 0 and self.ice_arrow_active_attacks == 0
        if skill_name == "blizzard":
            return not self.blizzard_used
        if skill_name == "frost_spear":
            return self.frost_spear_cooldown == 0
        return super().is_skill_available(skill_name)

    def on_turn_start(self):
        super().on_turn_start()
        if self.ice_arrow_cooldown > 0:
            self.ice_arrow_cooldown -= 1
        if self.frost_spear_cooldown > 0:
            self.frost_spear_cooldown -= 1

    def attack_target(self, target):
        if self.ice_arrow_active_attacks > 0:
            damage = self.attack * 40 // (100 + target.defense * 0.8) + 15
            if damage < 0:
                damage = 0
            print(f"{self.name} 射出冰晶箭矢，命中 {target.name}，造成 {int(damage)} 点伤害！")
            self.deal_damage(target, damage, attack_type="magical")
            if random.random() < 0.70:
                target.apply_freeze(1, source=self, type_name='freeze')
            self.ice_arrow_active_attacks -= 1
            if self.ice_arrow_active_attacks == 0:
                print(f"{self.name} 的冰晶箭矢效果结束了！")
            return
        super().attack_target(target)

    def level_up(self, announce=True):
        super().level_up(announce)
        self.maxHP += 14
        self.attack += 10
        self.defense += 4

    def settlement(self):
        super().settlement()
        self.ice_arrow_active_attacks = 0
        self.ice_arrow_cooldown = 0
        self.blizzard_used = False
        self.frost_spear_cooldown = 0

    def get_skill_runtime_info(self):
        return {
            "ice_arrow": f"cd={self.ice_arrow_cooldown}, charges={self.ice_arrow_active_attacks}",
            "blizzard": f"remaining={0 if self.blizzard_used else 1}",
            "frost_spear": f"cd={self.frost_spear_cooldown}",
        }

    def ice_arrow(self, target):
        if self.ice_arrow_active_attacks > 0:
            print(f"{self.name} 已处于冰晶箭矢强化状态！")
            return
        if self.ice_arrow_cooldown > 0:
            print(f"{self.name} 的冰晶箭矢仍在冷却中，还需 {self.ice_arrow_cooldown} 回合！")
            return
        self.ice_arrow_active_attacks = 2
        self.ice_arrow_cooldown = 4
        print(f"{self.name} 凝聚寒冰之力，接下来的 2 次普通攻击将附带冰晶箭矢效果！")

   
    def blizzard(self, target):
        if self.blizzard_used:
            print(f"{self.name} 的暴风雪是限定技，本场战斗已使用过！")
            return
        self.blizzard_used = True
        dot_damage = int(self.attack * 15 // (100 + target.defense * 0.8) + 10)
        target.apply_attack_down(0.20, 3, source_name=self.name)
        target.apply_continuous_damage(dot_damage, 3, source=self)
        print(f"{self.name} 召唤暴风雪，压制了 {target.name}的攻击力！")

    def frost_spear(self, target):
        if self.frost_spear_cooldown > 0:
            print(f"{self.name} 的寒霜长矛仍在冷却中，还需 {self.frost_spear_cooldown} 回合！")
            return
        damage = int(self.attack * 45 // (100 + target.defense * 0.6) + 15)
        if damage < 0:
            damage = 0
        print(f"{self.name} 投掷寒霜长矛，命中 {target.name}，造成 {damage} 点伤害！")
        self.deal_damage(target, damage, attack_type="magical")
        if random.random() < 0.30:
            target.apply_freeze(1, source=self, type_name='freeze')
        self.frost_spear_cooldown = 4


class ThunderWizard(Character):
    def __init__(self, name, level = 1, maxHP = 190, attack = 95, defense = 10):
        super().__init__(name, level, maxHP, attack, defense)
        self.maxMP = 50
        self.MP = self.maxMP
        self.static_field_cooldown = 0
        self.ball_lightning_cooldown = 0
        self.thunder_strike_cooldown = 0
        self.static_field_turns = 0
        self.thunder_strike_turns = 0
        self.learn_skill("static_field", self.static_field, "生成一个静电场，少量提高防御，且当受到敌人攻击时，概率麻痹敌人，下回合将无法行动，冷却5回合，消耗15MP")
        self.learn_skill("ball_lightning", self.ball_lightning, "球状闪电：对敌人造成伤害，概率分裂成多个小闪电造成额外攻击，冷却2回合，消耗15MP")
        self.learn_skill("thunder_strike", self.thunder_strike, "雷霆一击：对敌人造成大量伤害，给自身附加带电效果3回合，在攻击时会造成额外伤害，冷却3回合，消耗20MP")
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.MP = self.maxMP

    def is_skill_available(self, skill_name):
        if skill_name == "static_field":
            return self.MP >= 15 and self.static_field_cooldown == 0
        if skill_name == "ball_lightning":
            return self.MP >= 15 and self.ball_lightning_cooldown == 0
        if skill_name == "thunder_strike":
            return self.MP >= 20 and self.thunder_strike_cooldown == 0
        return super().is_skill_available(skill_name)
    
    def on_turn_start(self):
        super().on_turn_start()
        if self.static_field_cooldown > 0:
            self.static_field_cooldown -= 1
        if self.ball_lightning_cooldown > 0:
            self.ball_lightning_cooldown -= 1
        if self.thunder_strike_cooldown > 0:
            self.thunder_strike_cooldown -= 1
        if self.static_field_turns > 0:
            self.static_field_turns -= 1
            if self.static_field_turns == 0:
                print(f"{self.name} 的静电场效果结束了！")
                self.defense -= int(15 + self.level)  # 静电场结束时降低之前提升的防御
        if self.thunder_strike_turns > 0:
            self.thunder_strike_turns -= 1
            if self.thunder_strike_turns == 0:
                print(f"{self.name} 的带电效果结束了！")

    def before_take_damage(self, value, attacker, attack_type):
        if attack_type != "counterattack" and self.static_field_turns > 0:
            if random.random() < 0.4:  # 40%概率触发麻痹
                # 触发麻痹于攻击者；使用 source=self 以便打印来源名称并避免重复信息
                if attacker is not None and hasattr(attacker, 'apply_freeze'):
                    attacker.apply_freeze(1, source=self, type_name="numbness")
        return value
    
    def attack_target(self, target):
        super().attack_target(target)
        if self.thunder_strike_turns > 0:
            extra_damage = int(target.health * 0.03) + 10  # 带电效果造成额外伤害，基于目标当前生命值的3%加上固定值 
            print(f"{self.name} 的带电效果造成了额外 {extra_damage} 点伤害！")
            self.deal_damage(target, extra_damage, attack_type="magical")


    def static_field(self):
        if self.MP < 15:
            print(f"{self.name} 法力不足，无法施放静电场！")
            return
        if self.static_field_cooldown > 0:
            print(f"{self.name} 的静电场仍在冷却中，还需 {self.static_field_cooldown} 回合！")
            return
        self.MP -= 15
        self.static_field_turns = 3
        self.static_field_cooldown = 5
        self.defense += int(15 + self.level)  # 提高防御
        print(f"{self.name} 生成了一个静电场，持续3回合！受到攻击时有概率麻痹敌人！")

    def ball_lightning(self,target):
        if self.MP < 15:
            print(f"{self.name} 法力不足，无法施放球状闪电！")
            return
        if self.ball_lightning_cooldown > 0:
            print(f"{self.name} 的球状闪电仍在冷却中，还需 {self.ball_lightning_cooldown} 回合！")
            return
        self.MP -= 15
        damage = int(self.attack * 35 // (100 + target.defense * 0.8) + 10)
        print(f"{self.name} 施放了球状闪电，命中 {target.name}，造成 {damage} 点伤害！")
        self.deal_damage(target, damage, attack_type="magical")
        if random.random() < 0.6:  # 60%概率分裂成小闪电
            extra_attacks = random.randint(2, 4)  # 分裂成2-4个小闪电
            print(f"{self.name} 的球状闪电分裂成了 {extra_attacks} 个小闪电！")
            extra_damage = extra_attacks * 8  # 每个小闪电造成8点伤害
            self.deal_damage(target, extra_damage, attack_type="magical")
        self.ball_lightning_cooldown = 2
            
    def thunder_strike(self,target):
        if self.MP < 20:
            print(f"{self.name} 法力不足，无法施放雷霆一击！")
            return
        if self.thunder_strike_cooldown > 0:
            print(f"{self.name} 的雷霆一击仍在冷却中，还需 {self.thunder_strike_cooldown} 回合！")
            return
        self.MP -= 20
        damage = int(self.attack * 50 // (100 + target.defense * 0.8) + 20)
        print(f"{self.name} 施放了雷霆一击，命中 {target.name}，造成 {damage} 点伤害！")
        self.deal_damage(target, damage)
        self.thunder_strike_turns = 3
        self.thunder_strike_cooldown = 3
        print(f"{self.name} 进入了带电状态，持续3回合！攻击时会造成额外伤害！")

    def get_skill_runtime_info(self):
        return {
            "static_field": f"cd={getattr(self, 'static_field_cooldown', 0)}, turns={getattr(self, 'static_field_turns', 0)}",
            "ball_lightning": f"cd={getattr(self, 'ball_lightning_cooldown', 0)}",
            "thunder_strike": f"cd={getattr(self, 'thunder_strike_cooldown', 0)}, turns={getattr(self, 'thunder_strike_turns', 0)}",
        }

    def settlement(self):
        super().settlement()
        # 重置法力与技能相关状态
        self.MP = getattr(self, 'maxMP', getattr(self, 'MP', 0))
        self.static_field_cooldown = 0
        self.ball_lightning_cooldown = 0
        self.thunder_strike_cooldown = 0
        self.static_field_turns = 0
        self.thunder_strike_turns = 0

    def level_up(self, announce=True):
        super().level_up(announce)
        self.maxHP += 12
        self.attack += 11
        self.defense += 3
        self.maxMP += 2
        self.MP = self.maxMP