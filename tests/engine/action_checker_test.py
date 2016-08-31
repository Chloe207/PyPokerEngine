from tests.base_unittest import BaseUnitTest
from pypokerengine.engine.player import Player
from pypokerengine.engine.poker_constants import PokerConstants as Const
from pypokerengine.engine.action_checker import ActionChecker

class ActionCheckerTest(BaseUnitTest):

  """ the case when no action is done before """
  def test_check(self):
    players = self.__setup_clean_players()
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'call', 0))
    self.eq(0, ActionChecker.need_amount_for_action(players[0], 0))
    self.eq(0, ActionChecker.need_amount_for_action(players[1], 0))

  def test_call(self):
    players = self.__setup_clean_players()
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, 'call', 10))

  def test_too_small_raise(self):
    players = self.__setup_clean_players()
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, 'raise', 4))

  def test_legal_raise(self):
    players = self.__setup_clean_players()
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'raise', 5))

  """ the case when agree amount = $10, minimum bet = $15"""
  def test__fold(self):
    players = self.__setup_blind_players()
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'fold'))

  def test__call(self):
    players = self.__setup_blind_players()
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, 'call', 9))
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'call', 10))
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, 'call', 11))
    self.eq(5, ActionChecker.need_amount_for_action(players[0], 10))
    self.eq(0, ActionChecker.need_amount_for_action(players[1], 10))

  def test__raise(self):
    players = self.__setup_blind_players()
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, 'raise', 14))
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'raise', 15))
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, 'raise', 16))
    self.eq(10, ActionChecker.need_amount_for_action(players[0], 15))
    self.eq(5, ActionChecker.need_amount_for_action(players[1], 15))

  def test__short_of_money(self):
    players = self.__setup_blind_players()
    players[0].collect_bet(88)  # p1 stack is $7
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, "call", 10))
    self.true(ActionChecker._ActionChecker__is_illegal(players, 0, "call", 15))

  def test_small_blind_allin_raise(self):
    players = self.__setup_blind_players()
    self.false(ActionChecker._ActionChecker__is_illegal(players, 0, "raise", 100))

  def test_big_blind_allin_call(self):
    players = self.__setup_blind_players()
    players[0].add_action_history(Const.Action.RAISE, 100, 95)
    self.false(ActionChecker._ActionChecker__is_illegal(players, 1, "call", 100))
    players[1].collect_bet(1)
    self.true(ActionChecker._ActionChecker__is_illegal(players, 1, "call", 100))

  def test_allin_check_on_call(self):
    player = self.__setup_clean_players()[0]
    self.false(ActionChecker.is_allin(player, "call", 99))
    self.true(ActionChecker.is_allin(player, "call", 100))
    self.true(ActionChecker.is_allin(player, "call", 101))

  def test_allin_check_on_raise(self):
    player = self.__setup_clean_players()[0]
    self.false(ActionChecker.is_allin(player, "raise", 99))
    self.true(ActionChecker.is_allin(player, "raise", 100))
    self.false(ActionChecker.is_allin(player, "raise", 101))

  def test_allin_check_on_fold(self):
    player = self.__setup_clean_players()[0]
    self.false(ActionChecker.is_allin(player, "fold", 0))

  def test_correct_action_on_allin_call(self):
    players = self.__setup_clean_players()
    players[0].add_action_history(Const.Action.RAISE, 50, 50)
    players[1].add_action_history(Const.Action.BIG_BLIND)
    players[1].stack = 30
    action, bet_amount = ActionChecker.correct_action(players, 1, 'call', 50)
    self.eq('call', action)
    self.eq(40, bet_amount)

  def test_correct_action_on_allin_raise(self):
    players = self.__setup_clean_players()
    action, bet_amount = ActionChecker.correct_action(players, 0, 'raise', 100)
    self.eq('raise', action)
    self.eq(100, bet_amount)

  def test_correct_illegal_call(self):
    players = self.__setup_clean_players()
    action, bet_amount = ActionChecker.correct_action(players, 0, 'call', 10)
    self.eq('fold', action)
    self.eq(0, bet_amount)

  def test_correct_illegal_raise(self):
    players = self.__setup_clean_players()
    action, bet_amount = ActionChecker.correct_action(players, 0, 'raise', 101)
    self.eq('fold', action)
    self.eq(0, bet_amount)

  def test_correct_action_when_legal(self):
    players = self.__setup_clean_players()
    action, bet_amount = ActionChecker.correct_action(players, 0, 'call', 0)
    self.eq('call', action)
    self.eq(0, bet_amount)

  def test_correct_action_when_legal(self):
    players = self.__setup_clean_players()
    action, bet_amount = ActionChecker.correct_action(players, 0, 'raise', 100)
    self.eq('raise', action)
    self.eq(100, bet_amount)

  def test_legal_actions(self):
    players = self.__setup_blind_players()
    legal_actions = ActionChecker.legal_actions(players, 0)
    self.eq({"action":"fold", "amount":0}, legal_actions[0])
    self.eq({"action":"call", "amount":10}, legal_actions[1])
    self.eq({"action":"raise", "amount": { "min":15, "max":100} }, legal_actions[2])


  def __setup_clean_players(self):
    return [Player("uuid", 100) for  _ in range(2)]

  def __setup_blind_players(self):
    return [self.__create_blind_player(flg) for flg in [True, False]]

  def __create_blind_player(self, small_blind=True):
    name = "sb" if small_blind else "bb"
    blind = 5 if small_blind else 10
    player = Player("uuid", 100, name=name)
    player.add_action_history(Const.Action.RAISE, blind, 5)
    player.collect_bet(blind)
    player.pay_info.update_by_pay(blind)
    return player

