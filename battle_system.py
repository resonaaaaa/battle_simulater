import battle_character
import random
import inspect


def build_skill_call(actor, skill_name, opponent):
	"""根据技能签名构建调用参数。"""
	if skill_name == "attack":
		return skill_name, (opponent,), {}  

	skill = actor.skills.get(skill_name)
	if skill is None:
		return skill_name, (), {}
	if not callable(skill):
		return "attack", (opponent,), {}

	try:
		sig = inspect.signature(skill)
	except (ValueError, TypeError):
		# 内置或特殊可调用对象，默认传入对手
		return skill_name, (opponent,), {}

	if len(sig.parameters) == 0:
		return skill_name, (), {}
	return skill_name, (opponent,), {}


def default_strategy(actor, opponent):
	"""
	默认的技能选择策略函数。它会随机选择一个技能来使用，优先选择非基本攻击技能，但有一定概率直接使用基本攻击。
	函数会检查所选技能是否需要参数（如对手），如果需要则传递对手作为参数，否则不传递任何参数。
	最终返回所选技能的名称以及相应的参数。
	"""
	available_skills = actor.get_available_skills()
	if not available_skills:
		# 理论上不会发生，因为基础 attack 永远可用
		return "attack", (opponent,), {}

	non_attack = [s for s in available_skills if s != "attack"]
	if non_attack and random.random() < 0.5:
		choice = random.choice(non_attack)
	else:
		choice = "attack" if "attack" in available_skills else random.choice(available_skills)

	return build_skill_call(actor, choice, opponent)


def prompt_strategy(actor, opponent):
	"""交给用户输入技能选择的策略函数。它会显示当前角色的技能列表，
	并提示用户选择一个技能来使用。根据用户的输入，函数会返回相应的技能名称以及需要传递给技能函数的参数（如果有的话）。
	如果用户输入了一个未知的技能名称，函数会默认返回基本攻击技能。
	"""
	print(f"\n{actor.name} 的回合！可用技能如下：")
	available_skills = actor.get_available_skills()
	if not available_skills:
		print("当前没有可用技能，默认使用基础攻击（attack）")
		return "attack", (opponent,), {}

	i = 1
	for skill in available_skills:
		print(f"{i} - {skill}") 
		i += 1

	try:
		choice = int(input("请选择技能编号: ").strip()) - 1
	except ValueError:
		print("输入不是有效数字，默认使用基础攻击（attack）")
		return "attack", (opponent,), {}

	if choice < 0 or choice >= len(available_skills):
		print("无效选择，默认使用基础攻击（attack）")
		return "attack", (opponent,), {}

	selected_skill = available_skills[choice]
	return build_skill_call(actor, selected_skill, opponent)


class BattleSystem:
	def __init__(self, char1: battle_character.Character, char2: battle_character.Character):
		self.char1 = char1
		self.char2 = char2
		self.turn = 0

	def run(self, strat1=None, strat2=None, verbose=True, winner_reward_levels=1):
		"""
		运行战斗系统，直到其中一个角色被击败。
		strat1 和 strat2 分别是 char1 和 char2 的技能选择策略函数，如果没有提供则使用默认的随机策略。
		每个回合，系统会根据当前角色的策略函数选择一个技能来使用，并执行该技能。
		战斗结束后，系统会宣布获胜者，并可给获胜者奖励等级。
		"""
		while self.char1.is_alive() and self.char2.is_alive() and self.turn < 100:  # 增加回合限制以防止死循环
			actor = self.char1 if self.turn % 2 == 0 else self.char2
			opponent = self.char2 if actor is self.char1 else self.char1
			actor.on_turn_start()
			if not actor.can_act():
				if verbose:
					print(f"\n第 {self.turn + 1} 回合：{actor.name} 因控制效果跳过行动")
				self.turn += 1
				continue
			strat = strat1 if actor is self.char1 else strat2
			strat = strat or default_strategy
			name, args, kwargs = strat(actor, opponent)
			if verbose:
				print(f"\n第 {self.turn + 1} 回合：{actor.name} 使用了技能 '{name}'")
			try:
				actor.use_skill(name, *args, **kwargs)
			except Exception as e:
				if verbose:
					print(f"{actor.name} 无法使用技能 {name}：{e}")
			self.turn += 1

		if self.char1.is_alive() and not self.char2.is_alive():
			winner = self.char1
		elif self.char2.is_alive() and not self.char1.is_alive():
			winner = self.char2
		else:
			winner = None

		if winner:
			if verbose:
				print(f"\n=== {winner.name} 获胜！===")
			if winner_reward_levels > 0:
				if verbose:
					print(f"{winner.name} 战后获得 {winner_reward_levels} 级奖励！")
				winner.gain_levels(winner_reward_levels, announce=verbose)
				winner.settlement()  #重置状态以准备下一场战斗
		return winner

def demo():
	
	print("正在创建两个测试角色...")
	bers = battle_character.Berserker("Heracles", level=31)
	witch = battle_character.Mermaid("Circe", level=31)
	bs = BattleSystem(bers, witch)
	
	mode = input("选择模式：自动(a) / 手动(m) [a/m]: ").strip().lower()
	if mode == "m":
		bs.run(strat1=default_strategy, strat2=prompt_strategy, verbose=True, winner_reward_levels=1)
	else:
		bs.run(verbose=True, winner_reward_levels=1)


if __name__ == "__main__":
	demo()
