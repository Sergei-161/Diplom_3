from pages.base_page import BasePage
from locators.locators import AuthPageLocators, MainPageLocators
from data.urls import MainUrl, URLS
import allure


class LoginPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = MainUrl.MAIN_URL + URLS.url_login

    @allure.step('Открыть страницу авторизации')
    def open(self):
        self.driver.get(self.url)
        self.wait_for_page_load()

    @allure.step('Ввести email')
    def set_email(self, email):
        self.enter_text(AuthPageLocators.email_input, email)

    @allure.step('Ввести пароль')
    def set_password(self, password):
        self.enter_text(AuthPageLocators.password_input, password)

    @allure.step('Кликнуть на кнопку "Войти"')
    def click_login_button(self):
        # Перед кликом закрываем возможные модальные окна
        self.close_all_modals()
        self.click_button(AuthPageLocators.login_account_btn)

    @allure.step('Выполнить авторизацию пользователя')
    def login(self, email, password):
        self.set_email(email)
        self.set_password(password)
        self.click_login_button()
        self.wait_for_page_load()

    @allure.step('Проверить видимость формы авторизации')
    def is_auth_form_visible(self):
        return self.is_element_visible(AuthPageLocators.auth_form)

    @allure.step('Закрыть все открытые модальные окна')
    def close_all_modals(self):
        try:
            # Пробуем закрыть крестиком модального окна ингредиента
            if self.is_element_visible(MainPageLocators.close_ingredient_modal, timeout=1):
                self.click_button(MainPageLocators.close_ingredient_modal)

            # Пробуем закрыть через оверлей
            if self.is_element_visible(MainPageLocators.modal_overlay, timeout=1):
                self.click_button(MainPageLocators.modal_overlay)

        except Exception:
            # Любые неожиданные ошибки при закрытии модалок игнорируем,
            # чтобы не ронять тест, если модалки просто нет.
            pass
