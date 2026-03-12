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

        # 仅基础 Character 在这里直接补齐等级；子类会在各自 __init__ 末尾处理
        if self.__class__ is Character and level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
    
    def attack_target(self, target):
        damage = self.attack * 40 // (100 + target.defense*0.8)  
        if damage < 0:
            damage = 0
        print(f"{self.name} 攻击了 {target.name}，造成 {damage} 点伤害！")
        target.take_damage(damage)

    def is_alive(self):
        return self.health > 0
    
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

    def take_damage(self, value,attacker,attack_type = "normal"):
        self.health -= value
        print(f"{self.name} 受到了 {value} 点伤害！当前生命值：{self.health}")

    def health_regeneration(self,value):
        self.health += value
        print(f"{self.name} 恢复了 {value} 点生命值！当前生命值：{self.health}")

    def settlement(self):
        self.health = self.maxHP

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

    def learn_skill(self, skill_name, func):
        self.skills[skill_name] = func

class Berserker(Character):
    def __init__(self, name, level = 1, maxHP = 200, attack = 100, defense = 20):
        super().__init__(name, level, maxHP, attack, defense)
        self.rage = 0
        self.rage_flag = False
        self.unleash_rage_threshold = 20
        # 狂战士专属技能
        self.learn_skill("get_into_anger", self.get_into_anger)
        self.learn_skill("unleash_rage", self.unleash_rage)
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
        return super().is_skill_available(skill_name)

    def attack_target(self, target):
        super().attack_target(target)
        self.rage += 10

    def take_damage(self, value):
        super().take_damage(value)
        self.rage += 5

    def get_into_anger(self):
        if self.rage >= 50:
            self.attack = int(self.attack * 1.3)
            self.defense = int(self.defense * 0.7)
            print(f"{self.name} 进入狂怒！攻击提高，但防御下降！")
            self.rage = 0
            self.rage_flag = True
        else:
            print(f"{self.name} 怒气不足，无法进入狂怒状态！")

    def unleash_rage(self, target):
        if self.rage_flag and self.rage >= self.unleash_rage_threshold:
            damage = int(self.attack * 0.5 + 0.5 * self.rage) // (1 + target.defense*0.8/100)  # 狂怒释放伤害根据当前攻击力和怒气值计算，可以部分穿透目标防御
            self.rage = 0
            self.rage_flag = False
            if damage < 0:
                damage = 0
            print(f"{self.name} 对 {target.name} 释放怒焰，造成 {damage} 点伤害！")
            target.take_damage(damage)
        else:
            print(f"{self.name} 怒气不足或未进入狂怒状态，无法释放怒焰！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 14
        self.attack += 11
        self.defense += 3
    
    def settlement(self):
        if self.rage_flag:
            self.attack = int(self.attack / 1.3)
            self.defense = int(self.defense / 0.7)
        super().settlement()
        self.rage = 0
        self.rage_flag = False

class Vampire(Character):
    def __init__(self, name, level = 1, maxHP = 160, attack = 90, defense = 15):
        super().__init__(name, level, maxHP, attack, defense)
        self.blood_sucking_level = 1 + (level - 1) // 5
        self.bat_count = 0
        # 吸血鬼专属技能
        self.learn_skill("bat_summon", self.bat_summon)
        self.learn_skill("bat_bomb", self.bat_bomb)
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.bat_count = 0

    def is_skill_available(self, skill_name):
        if skill_name == "bat_summon":
            return self.bat_count < 3
        if skill_name == "bat_bomb":
            return self.bat_count > 0
        return super().is_skill_available(skill_name)

    def attack_target(self, target):
        damage = (self.attack * 40) // (100 + target.defense*0.8)
        print(f"{self.name} 攻击了 {target.name}，造成 {damage} 点伤害！")
        bat_damage = (self.bat_count * self.attack * 0.1) * 40 // (100 + target.defense*0.8) # 每只蝙蝠增加10%攻击力的伤害
        print(f"{self.name} 的蝙蝠追加了 {bat_damage} 点伤害！")
        damage += int(bat_damage)
        if damage < 0:
            damage = 0
        target.take_damage(damage)
        blood_sucked = int(damage * 0.2) + 5 + self.blood_sucking_level * 2
        print(f"{self.name} 吸血恢复了 {blood_sucked} 点生命值!") 
        self.health_regeneration(blood_sucked)


    def bat_summon(self):
        if self.bat_count < 3:
            self.bat_count += 1 
            print(f"{self.name} 召唤了一只蝙蝠！当前蝙蝠数量：{self.bat_count}") 
        else:
            print(f"{self.name} 的蝙蝠数量已达到上限！")
    
    def bat_bomb(self, target):
        if self.bat_count > 0:
            damage = int((self.bat_count * self.attack * 0.3 * 0.4) // (1 + target.defense*0.8/100))  # 每只蝙蝠增加30%攻击力的伤害
            print(f"{self.name} 引爆了 {self.bat_count} 只蝙蝠，对 {target.name} 造成 {damage} 点伤害！")
            target.take_damage(damage)
            self.bat_count = 0
        else:
            print(f"{self.name} 没有蝙蝠可用来引爆！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 13
        self.attack += 10
        self.defense += 4

    def settlement(self):
        super().settlement()
        self.bat_count = 0

class Knight(Character):
    def __init__(self, name, level = 1, maxHP = 250, attack = 70, defense = 30):
        super().__init__(name, level, maxHP, attack, defense)
        self.counterattack_chance = min(0.1 + (level - 1) // 5 * 0.04,0.4)
        self.sacred_crash_flag = False
        # 骑士专属技能
        self.learn_skill("counterattack", self.counterattack)
        self.learn_skill("sacred_crash", self.sacred_crash)
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP

    def is_skill_available(self, skill_name):
        if skill_name == "counterattack":
            return True  # 格挡技能始终可用，但成功率由 counterattack_chance 决定/
        if skill_name == "sacred_crash":
            return not self.sacred_crash_flag
        return super().is_skill_available(skill_name)

    def attack_target(self, target):
        super().attack_target(target)

    def take_damage(self, value):
        if self.counterattack():
            print(f"{self.name} 成功格挡了攻击，未受到伤害！")
            self.counterattack_active = False
            return
        else:
            print(f"{self.name} 格挡失败，受到全额伤害！")
            self.counterattack_active = False
            super().take_damage(value)

    def sacred_crash(self, target):
        if self.sacred_crash_flag:
            print(f"{self.name} 已经使用过神圣冲击了，无法再次使用！")
            return
        damage = int(self.attack * 0.4 + min(200,(self.maxHP - self.health)*0.25))// (1 + target.defense*0.8/100)  # 自身损失血量越多，伤害越高,最多增加200点伤害
        if damage < 0:
            damage = 0
        print(f"{self.name} 施放神圣冲击，对 {target.name} 造成 {damage} 点伤害！")
        target.take_damage(damage)
        self.sacred_crash_flag = True

    def counterattack(self):
        import random
        if random.random() < self.counterattack_chance:
            return True
        else:
            return False

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 15
        self.attack += 8
        self.defense += 6


    def settlement(self):
        super().settlement()
        self.counterattack_active = False


class DragonHuman(Character):
    def __init__(self, name, level= 1, maxHP = 220, attack = 90, defense = 25):
        super().__init__(name, level, maxHP, attack, defense)
        self.dragon_breath = 0
        self.max_dragon_breath = 50
        # 龙裔专属技能
        self.learn_skill("dragon_breath_attack", self.dragon_breath_attack)
        self.learn_skill("dragon_flame", self.dragon_flame)
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
    
    def attack_target(self, target):
        super().attack_target(target)
        self.dragon_breath += 10
        if self.dragon_breath > self.max_dragon_breath:
            self.dragon_breath = self.max_dragon_breath
    
    def dragon_flame(self,target):
        if self.dragon_breath >= 50:
            damage = min(300,target.maxHP * 0.2)   #对敌人造成敌人最大生命值20%，最多300点伤害
            damage = int(damage)
            self.dragon_breath = 0
            print(f"{self.name} 释放龙焰，对 {target.name} 造成 {damage} 点伤害！")
            target.take_damage(damage)

    def dragon_breath_attack(self,target):
        if self.dragon_breath >= 30:
            damage = self.dragon_breath * (self.level * 0.15 + 1) // (1 + target.defense*0.3/100)  # 龙息攻击伤害根据龙息值和等级提升，可以部分穿透目标防御
            self.dragon_breath = 0
            damage = int(damage)
            print(f"{self.name} 释放龙息，对 {target.name} 造成 {damage} 点伤害！")
            target.take_damage(damage)
        else:
            print("龙息值不足，无法释放龙息攻击！")

    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 13
        self.attack += 10
        self.defense += 5
        self.max_dragon_breath += 1
    
    def settlement(self):
        super().settlement()
        self.dragon_breath = 0

class FlameWitch(Character):
    def __init__(self, name, level = 1, maxHP = 180, attack = 100, defense = 10):
        super().__init__(name, level, maxHP, attack, defense)
        self.maxMP = 80
        self.MP = self.maxMP
        self.shield = 0
        # 炎术女巫专属技能
        self.learn_skill("flame_crash", self.flame_crash)
        self.learn_skill("flame_shield", self.flame_shield)
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.MP = self.maxMP
            self.shield = 0

    def is_skill_available(self, skill_name):
        if skill_name in {"flame_crash", "flame_shield"}:
            return self.MP >= 20
        return super().is_skill_available(skill_name)

    def flame_crash(self,target):
        if self.MP < 20:
            print(f"{self.name} 法力不足，无法施放烈焰冲击！")
            return
        self.MP -= 20
        
        print(f"{self.name} 施放烈焰冲击，对 {target.name} 造成 {self.attack*0.3+20} 点伤害！")
        target.take_damage(self.attack*0.3+20)
    
    def flame_shield(self):
        if self.MP < 20:
            print(f"{self.name} 法力不足，无法施放烈焰护盾！")
            return
        self.MP -= 20
        self.shield = int(self.maxHP * 0.10 + 30)
        print(f"{self.name} 施放烈焰护盾，获得 {self.shield} 点护盾值！")
    
    def take_damage(self, value):
        if self.shield > 0:
            blocked = min(self.shield, value)
            self.shield -= blocked
            remain = value - blocked
            if remain > 0:
                super().take_damage(remain)
            print(f"{self.name} 的护盾吸收了 {blocked} 点伤害，剩余护盾：{self.shield}")
            return
        super().take_damage(value)
    
    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxMP += 4
        self.attack += 10
        self.defense += 3
        self.maxHP += 12

    def settlement(self):
        super().settlement()
        self.MP = self.maxMP
        self.shield = 0

class Mermaid(Character):
    def __init__(self, name, level = 1, maxHP = 200, attack = 80, defense = 30):
        super().__init__(name, level, maxHP, attack, defense)
        self.water_control_level = 1 + (level - 1) // 5
        self.shield = 0
        self.remaining_songs = 2
        self.learn_skill("water_shield", self.water_shield)
        self.learn_skill("cure_song", self.cure_song)
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.shield = 0
            self.remaining_songs = 2

    def water_shield(self):
        self.shield = int(self.water_control_level * 20 + self.defense * 0.1)
        print(f"{self.name} 形成了水盾，获得 {self.shield} 点护盾值！")
    
    def take_damage(self, value):
        if self.shield > 0:
            blocked = min(self.shield, value)
            self.shield -= blocked
            remain = value - blocked
            if remain > 0:
                super().take_damage(remain)
            print(f"{self.name} 的水盾吸收了 {blocked} 点伤害，剩余水盾：{self.shield}")
            return
        else:
            super().take_damage(value)

    def cure_song(self):
        if self.remaining_songs > 0:
            heal_value = int(min(300, (self.maxHP - self.health) * 0.6))
            self.health_regeneration(heal_value)  #回复已损失生命值的60%，最多300点
            self.remaining_songs -= 1
            print(f"{self.name} 的歌声治愈动人！剩余歌谣次数：{self.remaining_songs}")
        else:
            print(f"治愈歌谣的次数已用完！")

    def is_skill_available(self, skill_name):
        if skill_name == "cure_song":
            return self.remaining_songs > 0
        return super().is_skill_available(skill_name)
    
    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 15
        self.attack += 9
        self.defense += 5
        self.water_control_level = 1 + (self.level - 1) // 5

    def settlement(self):
        super().settlement()
        self.shield = 0
        self.remaining_songs = 2

class WolfMan(Character):
    def __init__(self, name, level = 1, maxHP = 220, attack = 85, defense = 25):
        super().__init__(name, level, maxHP, attack, defense)
        self.wolf_evolution_flag = False
        self.learn_skill("wolf_evolution", self.wolf_evolution)
        self.learn_skill("bloody_bite", self.bloody_bite)
        if level > 1:
            self.gain_levels(level - 1, announce=False)
            self.health = self.maxHP
            self.wolf_evolution_flag = False

    
    def wolf_evolution(self):
        if self.health < self.maxHP * 0.4 and self.wolf_evolution_flag == False:
            print(f"{self.name} 进入狼人形态！攻击将部分无视防御！")
            self.wolf_evolution_flag = True
        else:
            print(f"{self.name} 无法进入狼人形态！")

    def attack_target(self, target):
        if self.wolf_evolution_flag == True:
            damage = self.attack * 40 // (100 + target.defense*0.4)  # 狼人形态部分无视防御
            print(f"{self.name} 狼化攻击了 {target.name}，造成 {int(damage)} 点伤害！")
            target.take_damage(damage)
        else:
            super().attack_target(target)
    
    def bloody_bite(self,target):
        damage = int(self.attack * 0.5 // (1 + target.defense*0.8/100))
        if target.health > target.maxHP * 0.5:
            bite_heal = int(damage * 0.3)
            print(f"{self.name} 使用血腥之咬，对 {target.name}造成了{damage} 点伤害，并吸取了 {bite_heal} 点生命值！")
            self.health_regeneration(bite_heal)
        else:
            print(f"{target.name}的生命值过低，无法吸取生命值！")
        target.take_damage(damage)


    def level_up(self, announce=True):
        super().level_up(announce=announce)
        self.maxHP += 14
        self.attack += 11
        self.defense += 4

    def settlement(self):
        super().settlement()
        self.wolf_evolution_flag = False